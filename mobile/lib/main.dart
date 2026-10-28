import 'package:flutter/material.dart';
import 'pf_demo.dart';

void main() {
  const demoEnabled = bool.fromEnvironment('FRC_PF_DEMO', defaultValue: false);
  runApp(const FRcaixinhaApp(demoEnabled: demoEnabled));
}

class FRcaixinhaApp extends StatelessWidget {
  const FRcaixinhaApp({
    super.key,
    this.demoEnabled = false,
    this.demoGateway,
    this.demoFixture = PfDemoFixture.sample,
  });

  final bool demoEnabled;
  final PfDemoGateway? demoGateway;
  final PfDemoFixture demoFixture;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FRcaixinha 2.2',
      home: demoEnabled
          ? PfDemoPage(
              gateway: demoGateway ?? const LocalPfDemoGateway(),
              fixture: demoFixture,
            )
          : const Scaffold(
              body: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'FRcaixinha 2.2',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 12),
                    Text('Base técnica em preparação'),
                  ],
                ),
              ),
            ),
    );
  }
}
