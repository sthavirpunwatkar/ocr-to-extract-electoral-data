import 'package:flutter/material.dart';
import 'dart:async';
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
  final APIService apiService = APIService(baseUrl: APIService.serverUrl);
  final DBService dbService = DBService();
  List<Voter> voters = [];
  List<Voter> filteredVoters = [];
  bool isLoading = false;
  final TextEditingController _searchController = TextEditingController();
  Timer? _debounce;
  final int candidateId = 1; // Default candidate ID

  @override
  void initState() {
    super.initState();
    _loadVoters();
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadVoters() async {
    if (mounted) setState(() => isLoading = true);
    try {
      final localVoters = await dbService.getAllVoters();
      if (mounted) {
        setState(() {
          voters = localVoters;
          filteredVoters = localVoters;
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load local data: $e')),
        );
      }
    }
  }

  void _onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      if (query.isEmpty) {
        setState(() {
          filteredVoters = voters;
        });
        return;
      }
      _performSearch(query);
    });
  }

  Future<void> _performSearch(String query) async {
    setState(() => isLoading = true);
    try {
      final results = await apiService.searchVoters(query, candidateId);
      if (mounted) {
        setState(() {
          filteredVoters = results;
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => isLoading = false);
        // Fallback to local filtering
        _filterVoters(query);
      }
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
      final remoteVoters = await apiService.fetchVoters(candidateId);
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
        final List<dynamic>? successIdsRaw = result['success'];
        final List<int> successIds = successIdsRaw?.map((e) => e as int).toList() ?? [];
        
        if (successIds.isNotEmpty) {
          await dbService.markAsSynced(successIds);
        }
        
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

    int totalVoters = voters.length;
    int supportiveCount = voters.where((v) => v.sentiment == 'Supportive').length;
    int neutralCount = voters.where((v) => v.sentiment == 'Neutral').length;
    int opposedCount = voters.where((v) => v.sentiment == 'Opposed').length;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Voter Dashboard', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
            Text('Sunil Punwatkar | Nagpur South West', style: TextStyle(color: Colors.white.withValues(alpha: 0.8), fontSize: 12)),
          ],
        ),
        backgroundColor: primaryColor,
        actions: [
          IconButton(icon: const Icon(Icons.sync, color: Colors.white), onPressed: _syncData),
          IconButton(icon: const Icon(Icons.refresh, color: Colors.white), onPressed: _refreshVoters),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  color: primaryColor,
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(child: _buildStatCard('Total', totalVoters.toString(), Colors.white)),
                          Expanded(child: _buildStatCard('Supportive', supportiveCount.toString(), Colors.greenAccent)),
                          Expanded(child: _buildStatCard('Neutral', neutralCount.toString(), Colors.grey)),
                          Expanded(child: _buildStatCard('Opposed', opposedCount.toString(), Colors.redAccent)),
                        ],
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _searchController,
                        onChanged: _onSearchChanged,
                        decoration: InputDecoration(
                          hintText: 'Search by Name or EPIC ID...',
                          prefixIcon: const Icon(Icons.search, color: primaryColor),
                          filled: true,
                          fillColor: Colors.white,
                          contentPadding: const EdgeInsets.symmetric(vertical: 0),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide: BorderSide.none,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: filteredVoters.length,
                    itemBuilder: (context, index) {
                      final voter = filteredVoters[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        elevation: 1,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        child: ListTile(
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          leading: CircleAvatar(
                            radius: 24,
                            backgroundColor: _getSentimentColor(voter.sentiment).withValues(alpha: 0.2),
                            child: Icon(_getSentimentIcon(voter.sentiment), color: _getSentimentColor(voter.sentiment), size: 28),
                          ),
                          title: Text(voter.fullName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 4.0),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.grey.shade200,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(voter.voterId, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                ),
                                const SizedBox(width: 8),
                                Icon(
                                  voter.isSynced ? Icons.cloud_done : Icons.cloud_off,
                                  size: 14,
                                  color: voter.isSynced ? Colors.green : Colors.orange,
                                ),
                              ],
                            ),
                          ),
                          trailing: const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey),
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
                ),
              ],
            ),
    );
  }

  Widget _buildStatCard(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(color: color, fontSize: 20, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white70, fontSize: 10),
        ),
      ],
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
