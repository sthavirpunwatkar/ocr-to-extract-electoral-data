class Voter {
  final int id;
  final String voterId;
  final String fullName;
  final String status;
  final String? sentiment;
  final String? notes;
  final int version;
  final double? latitude;
  final double? longitude;
  final String? updatedAt;
  final bool isSynced;

  Voter({
    required this.id,
    required this.voterId,
    required this.fullName,
    required this.status,
    this.sentiment,
    this.notes,
    required this.version,
    this.latitude,
    this.longitude,
    this.updatedAt,
    this.isSynced = true,
  });

  factory Voter.fromJson(Map<String, dynamic> json) {
    return Voter(
      id: json['id'],
      voterId: json['voter_id'] ?? '',
      fullName: json['full_name'] ?? '',
      status: json['status'] ?? 'Pending',
      sentiment: json['sentiment'],
      notes: json['notes'],
      version: json['version'] ?? 1,
      latitude: json['latitude'],
      longitude: json['longitude'],
      updatedAt: json['updated_at'],
      isSynced: true,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'voter_id': voterId,
      'full_name': fullName,
      'status': status,
      'sentiment': sentiment,
      'notes': notes,
      'version': version,
      'latitude': latitude,
      'longitude': longitude,
      'updated_at': updatedAt,
      'is_synced': isSynced ? 1 : 0,
    };
  }

  factory Voter.fromMap(Map<String, dynamic> map) {
    return Voter(
      id: map['id'],
      voterId: map['voter_id'],
      fullName: map['full_name'],
      status: map['status'],
      sentiment: map['sentiment'],
      notes: map['notes'],
      version: map['version'],
      latitude: map['latitude'],
      longitude: map['longitude'],
      updatedAt: map['updated_at'],
      isSynced: map['is_synced'] == 1,
    );
  }

  Voter copyWith({
    String? status,
    String? sentiment,
    String? notes,
    int? version,
    double? latitude,
    double? longitude,
    String? updatedAt,
    bool? isSynced,
  }) {
    return Voter(
      id: id,
      voterId: voterId,
      fullName: fullName,
      status: status ?? this.status,
      sentiment: sentiment ?? this.sentiment,
      notes: notes ?? this.notes,
      version: version ?? this.version,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      updatedAt: updatedAt ?? this.updatedAt,
      isSynced: isSynced ?? this.isSynced,
    );
  }
}
