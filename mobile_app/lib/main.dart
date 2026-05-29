import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

const String appTitle = String.fromEnvironment('APP_TITLE', defaultValue: 'Campaign Connect');
const String primaryColorHex = String.fromEnvironment('PRIMARY_COLOR', defaultValue: '0xFF003366');

void main() {
  runApp(const CampaignApp());
}

class CampaignApp extends StatelessWidget {
  const CampaignApp({super.key});

  @override
  Widget build(BuildContext context) {
    final int primaryColorInt = int.parse(primaryColorHex);
    return MaterialApp(
      title: appTitle,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: Color(primaryColorInt),
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Color(primaryColorInt),
          primary: Color(primaryColorInt),
          secondary: const Color(0xFFFF9933),
        ),
      ),
      home: const LoginScreen(),
    );
  }
}
