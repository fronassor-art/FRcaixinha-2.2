"""IN-07: inventário offline do risco de downgrade F2P4.

Não é um bloqueio instalado no Alembic, nem um validador suficiente
para SQL arbitrário. O downgrade existente continua DESTRUTIVO e BLOQUEADO
para uso operacional. Nenhuma conexão, migration ou remoção de dados ocorre.
"""
import ast
from dataclasses import dataclass
import inspect
import textwrap

from migrations.versions import f2p4_20261022_auth_bootstrap_draft as f2p4


@dataclass(frozen=True, slots=True)
class DowngradeRisk:
    revision: str
    drop_tables: tuple[str, ...]
    drop_indexes: tuple[str, ...]
    unknown_operations: tuple[str, ...]
    authorized_to_execute: bool = False

    @property
    def destructive(self) -> bool:
        return bool(self.drop_tables or self.drop_indexes or self.unknown_operations)


def audit_downgrade_source(source: str, revision_id: str) -> DowngradeRisk:
    """Enumera operações explícitas; um AST desconhecido também bloqueia.

    O scanner NÃO certifica DDL seguro: dynamic SQL, funções importadas,
    SQL arbitrário e side effects exigem auditoria manual independente.
    """
    if type(source) is not str or not source.strip() or type(revision_id) is not str:
        raise ValueError("DOWNGRADE_AUDIT_INVALID")
    try:
        tree = ast.parse(textwrap.dedent(source))
        functions = [
            node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "downgrade"
        ]
        if len(functions) != 1:
            raise ValueError
        tables: list[str] = []
        indexes: list[str] = []
        unknown: list[str] = []
        for node in ast.walk(functions[0]):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                owner = node.func.value.id
                action = node.func.attr
                if owner == "op" and action in ("drop_table", "drop_index"):
                    if node.args and isinstance(node.args[0], ast.Constant) and type(node.args[0].value) is str:
                        (tables if action == "drop_table" else indexes).append(node.args[0].value)
                    else:
                        unknown.append(action + "_DYNAMIC")
                elif owner == "op":
                    unknown.append(action)
                elif owner in ("sa", "sqlalchemy"):
                    unknown.append(owner + "." + action)
            elif isinstance(node.func, ast.Name) and node.func.id not in ("str", "tuple"):
                # Fail-closed for helper calls: could execute DDL indirectly.
                unknown.append(node.func.id)
        return DowngradeRisk(
            revision=revision_id,
            drop_tables=tuple(tables),
            drop_indexes=tuple(indexes),
            unknown_operations=tuple(unknown),
        )
    except Exception:
        raise ValueError("DOWNGRADE_AUDIT_INVALID") from None


def audit_current_f2p4_downgrade() -> DowngradeRisk:
    return audit_downgrade_source(
        inspect.getsource(f2p4.downgrade), f2p4.revision,
    )


def require_nondestructive_approval(report: DowngradeRisk) -> None:
    """Não há autorização para downgrade F2P4: falhar fechado SEM exceção.

    Este método não é invocado por Alembic. Futuro gate executável
    requer revisão e autorização específicas, além de proteção operacional.
    """
    if not isinstance(report, DowngradeRisk):
        raise ValueError("DOWNGRADE_AUDIT_INVALID")
    raise RuntimeError("F2P4_DOWNGRADE_NOT_AUTHORIZED")
