import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/voter.dart';

class APIService {
  final String baseUrl;
  static String? authToken; // Made static to persist across screen transitions if needed

  APIService({required this.baseUrl});

  void setToken(String token) {
    authToken = token;
  }

  Map<String, String> _getHeaders() {
    final headers = {'Content-Type': 'application/json'};
    if (authToken != null) {
      headers['Authorization'] = 'Bearer $authToken';
    }
    return headers;
  }

  Future<List<Voter>> fetchVoters() async {
    final response = await http.get(
      Uri.parse('$baseUrl/voters'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      List jsonResponse = json.decode(response.body);
      return jsonResponse.map((voter) => Voter.fromJson(voter)).toList();
    } else {
      throw Exception('Failed to load voters');
    }
  }

  Future<Map<String, dynamic>> syncVoters(List<Voter> updates, String deviceId) async {        
    final body = updates.map((v) => {
      'id': v.id,
      'status': v.status,
      'sentiment': v.sentiment,
      'notes': v.notes,
      'version': v.version,
      'latitude': v.latitude,
      'longitude': v.longitude,
      'device_id': deviceId,
      'updated_at': v.updatedAt ?? DateTime.now().toIso8601String(),
    }).toList();

    final response = await http.post(
      Uri.parse('$baseUrl/sync'),
      headers: _getHeaders(),
      body: json.encode(body),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to sync voters');
    }
  }
}
