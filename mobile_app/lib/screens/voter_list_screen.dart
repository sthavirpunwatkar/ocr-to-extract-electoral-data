import 'package:flutter/material.dart';
import '../models/voter.dart';
import '../services/api_service.dart';
import '../services/db_service.dart';
import 'voter_detail_screen.dart';

class VoterListScreen extends StatefulWidget {
  const VoterListScreen({super.key});

  @override
  State<VoterListScreen> createState() => _VoterListScreenState();
}

class _VoterListScreenState extends State<VoterListScreen> {
  final APIService apiService = APIService(baseUrl: 'http://10.0.2.2:8000');
  final DBService dbService = DBService();
  List<Voter> voters = [];
  List<Voter> filteredVoters = [];
  bool isLoading = false;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadVoters();
  }

  Future<void> _loadVoters() async {
    if (mounted) setState(() => isLoading = true);
    final localVoters = await dbService.getAllVoters();
    if (mounted) {
      setState(() {
        voters = localVoters;
        filteredVoters = localVoters;
        isLoading = false;
      });
    }
  }

  void _filterVoters(String query) {
    setState(() {
      filteredVoters = voters
          .where((v) =>
              v.fullName.toLowerCase().contains(query.toLowerCase()) ||
              v.voterId.toLowerCase().contains(query.toLowerCase()))
          .toList();
    });
  }

  Future<void> _refreshVoters() async {
    setState(() => isLoading = true);
    try {
      final remoteVoters = await apiService.fetchVoters();
      await dbService.insertVoters(remoteVoters);
      await _loadVoters();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  Future<void> _syncData() async {
    setState(() => isLoading = true);
    try {
      final unsynced = await dbService.getUnsyncedVoters();
      if (unsynced.isNotEmpty) {
        final result = await apiService.syncVoters(unsynced, 'device_001');
        List<dynamic> successIdsRaw = result['success'];
        List<int> successIds = successIdsRaw.cast<int>();
        await dbService.markAsSynced(successIds);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Synced ${successIds.length} records')),
        );
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No data to sync')),
        );
      }
      await _loadVoters();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Sync failed: $e')),
      );
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    const primaryColor = Color(0xFF003366); // Deep Blue
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voter Search', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: primaryColor,
        actions: [
          IconButton(icon: const Icon(Icons.sync, color: Colors.white), onPressed: _syncData),
          IconButton(icon: const Icon(Icons.refresh, color: Colors.white), onPressed: _refreshVoters),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(70),
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              onChanged: _filterVoters,
              decoration: InputDecoration(
                hintText: 'Search by Name or EPIC ID...',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
        ),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: filteredVoters.length,
              itemBuilder: (context, index) {
                final voter = filteredVoters[index];
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  elevation: 2,
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: _getSentimentColor(voter.sentiment),
                      child: Icon(_getSentimentIcon(voter.sentiment), color: Colors.white, size: 20),
                    ),
                    title: Text(voter.fullName, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('ID: ${voter.voterId}'),
                        Text('Status: ${voter.status}', 
                          style: TextStyle(color: voter.isSynced ? Colors.green : Colors.orange, fontWeight: FontWeight.w500)),
                      ],
                    ),
                    trailing: const Icon(Icons.chevron_right, color: primaryColor),
                    onTap: () async {
                      if (!mounted) return;
                      await Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => VoterDetailScreen(voter: voter),
                        ),
                      );
                      _loadVoters();
                    },
                  ),
                );
              },
            ),
    );
  }

  Color _getSentimentColor(String? sentiment) {
    switch (sentiment) {
      case 'Supportive': return Colors.green;
      case 'Neutral': return Colors.grey;
      case 'Opposed': return Colors.red;
      default: return Colors.blueGrey;
    }
  }

  IconData _getSentimentIcon(String? sentiment) {
    switch (sentiment) {
      case 'Supportive': return Icons.sentiment_very_satisfied;
      case 'Neutral': return Icons.sentiment_neutral;
      case 'Opposed': return Icons.sentiment_very_dissatisfied;
      default: return Icons.person;
    }
  }
}
