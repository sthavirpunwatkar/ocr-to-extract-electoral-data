import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/voter.dart';

class DBService {
  static final DBService _instance = DBService._internal();
  static Database? _database;

  DBService._internal();

  factory DBService() => _instance;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB();
    return _database!;
  }

  Future<Database> _initDB() async {
    String path = join(await getDatabasesPath(), 'voter_campaign.db');
    return await openDatabase(
      path,
      version: 2, // Incremented version
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE voters (
            id INTEGER PRIMARY KEY,
            voter_id TEXT,
            full_name TEXT,
            status TEXT,
            sentiment TEXT,
            notes TEXT,
            version INTEGER,
            latitude REAL,
            longitude REAL,
            updated_at TEXT,
            is_synced INTEGER
          )
        ''');
      },
      onUpgrade: (db, oldVersion, newVersion) async {
        if (oldVersion < 2) {
          await db.execute('ALTER TABLE voters ADD COLUMN sentiment TEXT');
          await db.execute('ALTER TABLE voters ADD COLUMN notes TEXT');
        }
      },
    );
  }

  Future<void> insertVoters(List<Voter> voters) async {
    final db = await database;
    final batch = db.batch();
    for (var voter in voters) {
      batch.insert(
        'voters',
        voter.toMap(),
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<List<Voter>> getAllVoters() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query('voters');
    return List.generate(maps.length, (i) => Voter.fromMap(maps[i]));
  }

  Future<void> updateVoter(Voter voter) async {
    final db = await database;
    await db.update(
      'voters',
      voter.toMap(),
      where: 'id = ?',
      whereArgs: [voter.id],
    );
  }

  Future<List<Voter>> getUnsyncedVoters() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'voters',
      where: 'is_synced = ?',
      whereArgs: [0],
    );
    return List.generate(maps.length, (i) => Voter.fromMap(maps[i]));
  }

  Future<void> markAsSynced(List<int> ids) async {
    final db = await database;
    final batch = db.batch();
    for (var id in ids) {
      batch.update(
        'voters',
        {'is_synced': 1},
        where: 'id = ?',
        whereArgs: [id],
      );
    }
    await batch.commit(noResult: true);
  }
}
