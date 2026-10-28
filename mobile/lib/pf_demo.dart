import 'package:flutter/material.dart';

/// Valores fixos de demonstração; a tela não aceita digitação de dados reais.
class PfDemoFixture {
  const PfDemoFixture({
    required this.name,
    required this.cpf,
    required this.email,
    required this.phone,
  });

  static const sample = PfDemoFixture(
    name: 'Pessoa Sintetica',
    cpf: '529.982.247-25',
    email: 'demo@example.com',
    phone: '(91) 91234-5678',
  );

  final String name;
  final String cpf;
  final String email;
  final String phone;
}

/// Porta local injetável. Nenhuma implementação deste lote usa HTTP ou disco.
abstract class PfDemoGateway {
  Future<void> submit(PfDemoFixture fixture);
}

class LocalPfDemoGateway implements PfDemoGateway {
  const LocalPfDemoGateway();

  @override
  Future<void> submit(PfDemoFixture fixture) async {
    if (!identical(fixture, PfDemoFixture.sample)) {
      throw StateError('DEMO_FIXTURE_ONLY');
    }
  }
}

class PfDemoPage extends StatefulWidget {
  const PfDemoPage({
    super.key,
    required this.gateway,
    this.fixture = PfDemoFixture.sample,
  });

  final PfDemoGateway gateway;
  final PfDemoFixture fixture;

  @override
  State<PfDemoPage> createState() => _PfDemoPageState();
}

class _PfDemoPageState extends State<PfDemoPage> {
  final _formKey = GlobalKey<FormState>();
  bool _submitting = false;
  String? _result;

  bool _validCpf(String value) {
    if (!RegExp(r'^(\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$').hasMatch(value)) {
      return false;
    }
    final digits = value.replaceAll(RegExp(r'\D'), '');
    if (digits.split('').toSet().length == 1) return false;
    for (var length = 9; length <= 10; length++) {
      var sum = 0;
      for (var i = 0; i < length; i++) {
        sum += int.parse(digits[i]) * (length + 1 - i);
      }
      var check = (sum * 10) % 11;
      if (check == 10) check = 0;
      if (check != int.parse(digits[length])) return false;
    }
    return true;
  }

  String? _validateName(String? value) {
    final name = value?.trim() ?? '';
    if (name.isEmpty ||
        name.length > 200 ||
        RegExp(r'[\x00-\x1f\x7f]').hasMatch(name) ||
        !RegExp(r'[A-Za-zÀ-ÿ]').hasMatch(name)) {
      return 'Nome sintético inválido';
    }
    return null;
  }

  String? _validateCpf(String? value) =>
      _validCpf(value ?? '') ? null : 'CPF sintético inválido';

  String? _validateEmail(String? value) {
    final email = value ?? '';
    if (email.length > 254 ||
        !RegExp(
          r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
        ).hasMatch(email)) {
      return 'E-mail sintético inválido';
    }
    return null;
  }

  String? _validatePhone(String? value) {
    final phone = value ?? '';
    if (!RegExp(
      r'^(\d{10,11}|\(\d{2}\) \d{4,5}-\d{4}|\d{2} \d{4,5}-\d{4})$',
    ).hasMatch(phone)) {
      return 'Telefone sintético inválido';
    }
    final digits = phone.replaceAll(RegExp(r'\D'), '');
    final ddd = int.tryParse(digits.substring(0, 2));
    const validDdds = {
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      21,
      22,
      24,
      27,
      28,
      31,
      32,
      33,
      34,
      35,
      37,
      38,
      41,
      42,
      43,
      44,
      45,
      46,
      47,
      48,
      49,
      51,
      53,
      54,
      55,
      61,
      62,
      63,
      64,
      65,
      66,
      67,
      68,
      69,
      71,
      73,
      74,
      75,
      77,
      79,
      81,
      82,
      83,
      84,
      85,
      86,
      87,
      88,
      89,
      91,
      92,
      93,
      94,
      95,
      96,
      97,
      98,
      99,
    };
    if (!validDdds.contains(ddd)) return 'Telefone sintético inválido';
    final subscriber = digits.substring(2);
    if ((subscriber.length == 9 && subscriber.startsWith('9')) ||
        (subscriber.length == 8 && '2345'.contains(subscriber[0]))) {
      return null;
    }
    return 'Telefone sintético inválido';
  }

  Future<void> _submit() async {
    if (_submitting) return;
    if (!_formKey.currentState!.validate()) {
      setState(() => _result = 'Confira os dados fictícios exibidos.');
      return;
    }
    setState(() {
      _submitting = true;
      _result = null;
    });
    try {
      await widget.gateway.submit(widget.fixture);
      if (!mounted) return;
      setState(
        () => _result =
            'Solicitação demonstrativa recebida. Nenhum cadastro ou acesso foi criado.',
      );
    } catch (_) {
      if (!mounted) return;
      setState(
        () => _result = 'Demonstração indisponível. Nenhum dado foi enviado.',
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Widget _field(
    String label,
    String value,
    FormFieldValidator<String> validator,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        initialValue: value,
        readOnly: true,
        enableInteractiveSelection: false,
        decoration: InputDecoration(
          labelText: label,
          helperText: 'Exemplo fictício, somente leitura',
          border: const OutlineInputBorder(),
        ),
        validator: validator,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final fixture = widget.fixture;
    return Scaffold(
      appBar: AppBar(title: const Text('FRcaixinha 2.2')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 560),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Semantics(
                    label: 'Modo demonstração, dados fictícios',
                    child: Card(
                      color: Color(0xFFFFF3CD),
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Text(
                          'MODO DEMONSTRAÇÃO — DADOS FICTÍCIOS',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Pré-cadastro PF',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Esta tela usa exemplos fixos. Não digite dados pessoais reais. '
                    'Nenhum cadastro, identidade ou acesso será ativado.',
                  ),
                  const SizedBox(height: 20),
                  _field('Nome', fixture.name, _validateName),
                  _field('CPF', fixture.cpf, _validateCpf),
                  _field('E-mail', fixture.email, _validateEmail),
                  _field('Telefone', fixture.phone, _validatePhone),
                  const SizedBox(height: 8),
                  FilledButton(
                    key: const Key('pf-demo-submit'),
                    onPressed: _submitting ? null : _submit,
                    child: const Text('Simular envio'),
                  ),
                  if (_submitting) ...[
                    const SizedBox(height: 12),
                    const Center(child: CircularProgressIndicator()),
                  ],
                  if (_result != null) ...[
                    const SizedBox(height: 12),
                    Text(_result!, key: const Key('pf-demo-result')),
                  ],
                  const SizedBox(height: 16),
                  const Text(
                    'Cadastro e acesso real ainda não estão habilitados.',
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
