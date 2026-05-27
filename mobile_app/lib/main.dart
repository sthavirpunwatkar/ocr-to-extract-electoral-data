import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const CampaignApp());
}

class CampaignApp extends StatelessWidget {
  const CampaignApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Campaign Connect',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFF003366),
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF003366),
          primary: const Color(0xFF003366),
          secondary: const Color(0xFFFF9933),
        ),
      ),
      home: const LoginScreen(),
    );
  }
}
