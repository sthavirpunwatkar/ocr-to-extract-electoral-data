import 'package:flutter_test/flutter_test.dart';
import 'package:campaign_app/main.dart';

void main() {
  testWidgets('Login Screen UI Test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const CampaignApp());

    // Verify that the login screen widgets are present.
    expect(find.text('CAMPAIGN CONNECT'), findsOneWidget);
    expect(find.text('LOGIN'), findsOneWidget);
  });
}
