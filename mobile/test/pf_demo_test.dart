import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frcaixinha/main.dart';
import 'package:frcaixinha/pf_demo.dart';

class RecordingDemoGateway implements PfDemoGateway {
  RecordingDemoGateway({this.pending, this.fail = false});

  final Completer<void>? pending;
  final bool fail;
  int calls = 0;

  @override
  Future<void> submit(PfDemoFixture fixture) async {
    calls++;
    if (fail) throw StateError('synthetic internal error');
    if (pending != null) await pending!.future;
  }
}

void main() {
  testWidgets('modo padrão não apresenta a tela de pré-cadastro', (
    tester,
  ) async {
    await tester.pumpWidget(const FRcaixinhaApp());
    expect(find.byType(PfDemoPage), findsNothing);
    expect(find.text('Base técnica em preparação'), findsOneWidget);
    expect(find.text('Simular envio'), findsNothing);
  });

  testWidgets('tela opt-in mostra somente exemplos fixos e aviso permanente', (
    tester,
  ) async {
    final gateway = RecordingDemoGateway();
    await tester.pumpWidget(
      FRcaixinhaApp(demoEnabled: true, demoGateway: gateway),
    );
    expect(find.text('MODO DEMONSTRAÇÃO — DADOS FICTÍCIOS'), findsOneWidget);
    expect(find.text('Pré-cadastro PF'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(4));
    for (final field in tester.widgetList<EditableText>(
      find.byType(EditableText),
    )) {
      expect(field.readOnly, isTrue);
      expect(field.enableInteractiveSelection, isFalse);
    }
    expect(gateway.calls, 0);
  });

  testWidgets('envio sintético exibe processamento e reconhecimento neutro', (
    tester,
  ) async {
    final pending = Completer<void>();
    final gateway = RecordingDemoGateway(pending: pending);
    await tester.pumpWidget(
      FRcaixinhaApp(demoEnabled: true, demoGateway: gateway),
    );
    final button = find.byKey(const Key('pf-demo-submit'));
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(gateway.calls, 1);
    expect(tester.widget<FilledButton>(button).onPressed, isNull);
    pending.complete();
    await tester.pumpAndSettle();
    expect(
      find.textContaining('Solicitação demonstrativa recebida'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Nenhum cadastro ou acesso foi criado'),
      findsOneWidget,
    );
    expect(find.text('MODO DEMONSTRAÇÃO — DADOS FICTÍCIOS'), findsOneWidget);
  });

  testWidgets('entrada sintética inválida bloqueia envio', (tester) async {
    final gateway = RecordingDemoGateway();
    const invalid = PfDemoFixture(
      name: '1234',
      cpf: '529.982.247-26',
      email: 'invalid',
      phone: '00912345678',
    );
    await tester.pumpWidget(
      FRcaixinhaApp(
        demoEnabled: true,
        demoGateway: gateway,
        demoFixture: invalid,
      ),
    );
    final button = find.byKey(const Key('pf-demo-submit'));
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pump();
    expect(gateway.calls, 0);
    expect(find.text('Confira os dados fictícios exibidos.'), findsOneWidget);
    expect(find.text('Nome sintético inválido'), findsOneWidget);
    expect(find.text('CPF sintético inválido'), findsOneWidget);
    expect(find.text('E-mail sintético inválido'), findsOneWidget);
    expect(find.text('Telefone sintético inválido'), findsOneWidget);
  });

  testWidgets('falha do serviço não revela causa nem concede acesso', (
    tester,
  ) async {
    final gateway = RecordingDemoGateway(fail: true);
    await tester.pumpWidget(
      FRcaixinhaApp(demoEnabled: true, demoGateway: gateway),
    );
    final button = find.byKey(const Key('pf-demo-submit'));
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(gateway.calls, 1);
    expect(
      find.text('Demonstração indisponível. Nenhum dado foi enviado.'),
      findsOneWidget,
    );
    expect(find.textContaining('synthetic internal error'), findsNothing);
    expect(
      find.text('Cadastro e acesso real ainda não estão habilitados.'),
      findsOneWidget,
    );
  });

  test(
    'porta local rejeita qualquer fixture diferente da autorizada',
    () async {
      const gateway = LocalPfDemoGateway();
      await gateway.submit(PfDemoFixture.sample);
      await expectLater(
        gateway.submit(
          const PfDemoFixture(
            name: 'Pessoa Sintetica',
            cpf: '529.982.247-26',
            email: 'demo@example.com',
            phone: '(91) 91234-5678',
          ),
        ),
        throwsStateError,
      );
    },
  );
}
