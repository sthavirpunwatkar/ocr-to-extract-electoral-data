import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/voter.dart';

class APIService {
  static const String serverUrl = 'http://10.0.2.2:8000';
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

  Future<List<Voter>> fetchVoters(int candidateId) async {
    final uri = Uri.parse('$baseUrl/voters').replace(queryParameters: {
      'candidate_id': candidateId.toString(),
    });
    final response = await http.get(uri, headers: _getHeaders());
    if (response.statusCode == 200) {
      List jsonResponse = json.decode(utf8.decode(response.bodyBytes));
      return jsonResponse.map((voter) => Voter.fromJson(voter)).toList();
    } else {
      throw Exception('Failed to load voters');
    }
  }

  Future<List<Voter>> searchVoters(String query, int candidateId) async {
    final uri = Uri.parse('$baseUrl/search').replace(queryParameters: {
      'q': query,
      'candidate_id': candidateId.toString(),
    });
    final response = await http.get(uri, headers: _getHeaders());
    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(utf8.decode(response.bodyBytes));
      final List results = data['results'];
      return results.map((voter) => Voter.fromJson(voter)).toList();
    } else {
      throw Exception('Failed to search voters');
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
      return json.decode(utf8.decode(response.bodyBytes));
    } else {
      throw Exception('Failed to sync voters');
    }
  }
}
