import 'package:flutter/material.dart';

void main() {
  runApp(const FRcaixinhaApp());
}

class FRcaixinhaApp extends StatelessWidget {
  const FRcaixinhaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'FRcaixinha 2.2',
      home: Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'FRcaixinha 2.2',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
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
