/*
 Navicat Premium Dump Script

 Source Server         : timeline
 Source Server Type    : MongoDB
 Source Server Version : 80009 (8.0.9)
 Source Host           : localhost:27017
 Source Schema         : timeline

 Target Server Type    : MongoDB
 Target Server Version : 80009 (8.0.9)
 File Encoding         : 65001

 Date: 15/05/2025 20:17:23
*/


// ----------------------------
// Collection structure for events
// ----------------------------
db.getCollection("events").drop();
db.createCollection("events");

// ----------------------------
// Documents of events
// ----------------------------
db.getCollection("events").insert([ {
    _id: ObjectId("6825daeb35577cd93201c38f"),
    title: "{\"en\":\"Construction of Pyramids\",\"zh\":\"金字塔建造\"}",
    period: "ancient",
    date: "{\"start\":\"-2600-01-01\",\"end\":\"-2500-12-31\"}",
    location: "{\"coordinates\":[29.9792,31.1342],\"zoomLevel\":4,\"highlightColor\":\"#FF0000\"}",
    description: "{\"en\":\"Construction of the Great Pyramids of Giza\",\"zh\":\"吉萨大金字塔的建造时期\"}",
    media: "{\"images\":[\"pyramid.jpg\"],\"videos\":[\"pyramid.mp4\"],\"audios\":[\"pyramid.mp3\"],\"thumbnail\":\"pyramid-thumb.jpg\"}",
    contentRefs: "{\"articles\":[],\"images\":[],\"videos\":[],\"documents\":[]}",
    tags: "{\"category\":[\"architecture\",\"ancient\"],\"keywords\":[\"egypt\",\"wonders\"]}",
    importance: Int32("5"),
    is_public: true,
    last_updated: ISODate("2025-05-15T13:47:55.123Z"),
    created_at: ISODate("2025-05-15T13:47:55.123Z")
} ]);
db.getCollection("events").insert([ {
    _id: ObjectId("6825daeb35577cd93201c390"),
    title: "{\"en\":\"Roman Empire\",\"zh\":\"罗马帝国\"}",
    period: "ancient",
    date: "{\"start\":\"-27-01-16\",\"end\":\"476-09-04\"}",
    location: "{\"coordinates\":[41.9028,12.4964],\"zoomLevel\":3,\"highlightColor\":\"#FF0000\"}",
    description: "{\"en\":\"Rise and fall of the Roman Empire\",\"zh\":\"罗马帝国的兴衰\"}",
    media: "{\"images\":[\"Roman.jpg\"],\"videos\":[\"Roman.mp4\"],\"audios\":[\"Roman.mp3\"],\"thumbnail\":\"Roman-thumb.jpg\"}",
    contentRefs: "{\"articles\":[],\"images\":[],\"videos\":[],\"documents\":[]}",
    tags: "{\"category\":[\"empire\",\"ancient\"],\"keywords\":[\"rome\",\"europe\"]}",
    importance: Int32("5"),
    is_public: true,
    last_updated: ISODate("2025-05-15T13:47:55.123Z"),
    created_at: ISODate("2025-05-15T13:47:55.123Z")
} ]);
db.getCollection("events").insert([ {
    _id: ObjectId("6825daeb35577cd93201c391"),
    title: "{\"en\":\"Great Wall Construction\",\"zh\":\"长城修建\"}",
    period: "medieval",
    date: "{\"start\":\"1368-01-01\",\"end\":\"1644-12-31\"}",
    location: "{\"coordinates\":[110,35],\"zoomLevel\":4,\"highlightColor\":\"#FF0000\"}",
    description: "{\"en\":\"Ming Dynasty reconstruction of the Great Wall\",\"zh\":\"明朝时期长城的重建\"}",
    media: "{\"images\":[\"GreatWall.jpg\"],\"videos\":[\"GreatWall.mp4\"],\"audios\":[\"GreatWall.mp3\"],\"thumbnail\":\"GreatWall-thumb.jpg\"}",
    contentRefs: "{\"articles\":[],\"images\":[],\"videos\":[],\"documents\":[]}",
    tags: "{\"category\":[\"architecture\",\"defense\"],\"keywords\":[\"china\",\"ming\"]}",
    importance: Int32("4"),
    is_public: true,
    last_updated: ISODate("2025-05-15T13:47:55.123Z"),
    created_at: ISODate("2025-05-15T13:47:55.123Z")
} ]);
db.getCollection("events").insert([ {
    _id: ObjectId("6825daeb35577cd93201c392"),
    title: "{\"en\":\"Industrial Revolution\",\"zh\":\"工业革命\"}",
    period: "modern",
    date: "{\"start\":\"1760-01-01\",\"end\":\"1840-12-31\"}",
    location: "{\"coordinates\":[51.5074,-0.1278],\"zoomLevel\":3,\"highlightColor\":\"#FF0000\"}",
    description: "{\"en\":\"Transition to new manufacturing processes\",\"zh\":\"新型制造工艺的转型时期\"}",
    media: "{\"images\":[\"IndustrialRevolution.jpg\"],\"videos\":[\"IndustrialRevolution.mp4\"],\"audios\":[\"IndustrialRevolution.mp3\"],\"thumbnail\":\"IndustrialRevolution-thumb.jpg\"}",
    contentRefs: "{\"articles\":[],\"images\":[],\"videos\":[],\"documents\":[]}",
    tags: "{\"category\":[\"technology\",\"economy\"],\"keywords\":[\"britain\",\"invention\"]}",
    importance: Int32("4"),
    is_public: true,
    last_updated: ISODate("2025-05-15T13:47:55.123Z"),
    created_at: ISODate("2025-05-15T13:47:55.123Z")
} ]);

// ----------------------------
// Collection structure for periods
// ----------------------------
db.getCollection("periods").drop();
db.createCollection("periods");

// ----------------------------
// Documents of periods
// ----------------------------
db.getCollection("periods").insert([ {
    _id: ObjectId("6825db1435577cd93201c393"),
    periodId: "prehistoric",
    name: "{\"en\":\"Prehistoric\",\"zh\":\"史前时期\"}",
    description: "{\"en\":\"The period before written records, covering the origins of human civilization.\",\"zh\":\"有文字记录之前的时期，涵盖人类文明的起源\"}",
    startYear: Int32("-10000"),
    endYear: Int32("-3500"),
    color: "#8B4513",
    created_at: ISODate("2025-05-15T13:47:10.123Z")
} ]);
db.getCollection("periods").insert([ {
    _id: ObjectId("6825db1435577cd93201c394"),
    periodId: "ancient",
    name: "{\"en\":\"Ancient Civilizations\",\"zh\":\"古代文明\"}",
    description: "{\"en\":\"The rise of early civilizations with written records and organized societies.\",\"zh\":\"有文字记录和组织社会的早期文明兴起时期\"}",
    startYear: Int32("-3500"),
    endYear: Int32("500"),
    color: "#CD5C5C",
    created_at: ISODate("2025-05-15T13:47:10.123Z")
} ]);
db.getCollection("periods").insert([ {
    _id: ObjectId("6825db1435577cd93201c395"),
    periodId: "medieval",
    name: "{\"en\":\"Medieval\",\"zh\":\"中世纪\"}",
    description: "{\"en\":\"The period between ancient and modern times, characterized by feudalism and religious influence.\",\"zh\":\"古代和现代之间的时期，以封建制度和宗教影响为特征\"}",
    startYear: Int32("500"),
    endYear: Int32("1500"),
    color: "#4682B4",
    created_at: ISODate("2025-05-15T13:47:10.123Z")
} ]);
db.getCollection("periods").insert([ {
    _id: ObjectId("6825db1435577cd93201c396"),
    periodId: "modern",
    name: "{\"en\":\"Modern\",\"zh\":\"近现代\"}",
    description: "{\"en\":\"The period from the Renaissance to the present day, marked by industrialization and globalization.\",\"zh\":\"从文艺复兴到现代的时期，以工业化和全球化为标志\"}",
    startYear: Int32("1500"),
    endYear: Int32("2025"),
    color: "#32CD32",
    created_at: ISODate("2025-05-15T13:47:10.123Z")
} ]);

// ----------------------------
// Collection structure for regions
// ----------------------------
db.getCollection("regions").drop();
db.createCollection("regions");

// ----------------------------
// Documents of regions
// ----------------------------
db.getCollection("regions").insert([ {
    _id: ObjectId("6825db3435577cd93201c397"),
    name: "{\"en\":\"Mediterranean\",\"zh\":\"地中海\"}",
    description: "{\"en\":\"The Mediterranean region was central to ancient trade and cultural exchange.\",\"zh\":\"地中海地区是古代贸易和文化交流的中心\"}",
    boundary: "{\"type\":\"Polygon\",\"coordinates\":{\"\":{\"\":[30,10]}}}",
    period_id: "65d4f8e3a1b2c3d4e5f6a7b9",
    color: "#4CAF50",
    created_at: ISODate("2025-05-15T13:45:47.123Z")
} ]);
db.getCollection("regions").insert([ {
    _id: ObjectId("6825db3435577cd93201c398"),
    name: "{\"en\":\"Yellow River Valley\",\"zh\":\"黄河流域\"}",
    description: "{\"en\":\"The cradle of ancient Chinese civilization.\",\"zh\":\"中国古代文明的摇篮\"}",
    boundary: "{\"type\":\"Polygon\",\"coordinates\":{\"\":{\"\":[110,35]}}}",
    period_id: "65d4f8e3a1b2c3d4e5f6a7b9",
    color: "#FFC107",
    created_at: ISODate("2025-05-15T13:45:47.123Z")
} ]);
