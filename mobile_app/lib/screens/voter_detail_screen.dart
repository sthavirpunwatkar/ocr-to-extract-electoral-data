import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../models/voter.dart';
import '../services/db_service.dart';

class VoterDetailScreen extends StatefulWidget {
  final Voter voter;

  const VoterDetailScreen({super.key, required this.voter});

  @override
  State<VoterDetailScreen> createState() => _VoterDetailScreenState();
}

class _VoterDetailScreenState extends State<VoterDetailScreen> {
  late String _status;
  String? _sentiment;
  final TextEditingController _notesController = TextEditingController();
  double? _lat;
  double? _lng;
  final DBService dbService = DBService();

  @override
  void initState() {
    super.initState();
    _status = widget.voter.status;
    _sentiment = widget.voter.sentiment;
    _notesController.text = widget.voter.notes ?? '';
    _lat = widget.voter.latitude;
    _lng = widget.voter.longitude;
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _getLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    Position position = await Geolocator.getCurrentPosition();
    setState(() {
      _lat = position.latitude;
      _lng = position.longitude;
    });
  }

  Future<void> _save() async {
    final updatedVoter = widget.voter.copyWith(
      status: _status,
      sentiment: _sentiment,
      notes: _notesController.text,
      latitude: _lat,
      longitude: _lng,
      isSynced: false,
      updatedAt: DateTime.now().toIso8601String(),
    );
    await dbService.updateVoter(updatedVoter);
    if (!mounted) return;
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    const primaryColor = Color(0xFF003366); // Deep Blue
    const accentColor = Color(0xFFFF9933);  // Saffron

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.voter.fullName, style: const TextStyle(color: Colors.white)),
        backgroundColor: primaryColor,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('EPIC ID: ${widget.voter.voterId}', 
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    const Text('Address: Sample Address 123, Ward 5', 
                      style: TextStyle(fontSize: 16, color: Colors.grey)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text('Visit Status', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            DropdownButtonFormField<String>(
              value: _status,
              decoration: const InputDecoration(border: OutlineInputBorder()),
              items: ['Pending', 'Visited', 'Confirmed', 'Shifted', 'Deceased']
                  .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                  .toList(),
              onChanged: (val) => setState(() => _status = val!),
            ),
            const SizedBox(height: 20),
            const Text('Voter Sentiment', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _sentimentButton('Supportive', Colors.green, Icons.sentiment_very_satisfied),
                _sentimentButton('Neutral', Colors.grey, Icons.sentiment_neutral),
                _sentimentButton('Opposed', Colors.red, Icons.sentiment_very_dissatisfied),
              ],
            ),
            const SizedBox(height: 20),
            const Text('Notes', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            TextField(
              controller: _notesController,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText: 'Enter specific issues or requirements...',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                const Icon(Icons.location_on, color: primaryColor),
                const SizedBox(width: 8),
                Text('GPS: ${_lat?.toStringAsFixed(4) ?? "N/A"}, ${_lng?.toStringAsFixed(4) ?? "N/A"}'),
                const Spacer(),
                TextButton.icon(
                  onPressed: _getLocation, 
                  icon: const Icon(Icons.my_location), 
                  label: const Text('Capture Location'),
                ),
              ],
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: accentColor,
                  foregroundColor: Colors.white,
                  textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                onPressed: _save, 
                child: const Text('SAVE VISIT DATA'),      
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _sentimentButton(String label, Color color, IconData icon) {
    bool isSelected = _sentiment == label;
    return GestureDetector(
      onTap: () => setState(() => _sentiment = label),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isSelected ? color : color.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(color: color, width: 2),
            ),
            child: Icon(icon, color: isSelected ? Colors.white : color, size: 30),
          ),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(color: color, fontWeight: isSelected ? FontWeight.bold : FontWeight.normal)),
        ],
      ),
    );
  }
}
