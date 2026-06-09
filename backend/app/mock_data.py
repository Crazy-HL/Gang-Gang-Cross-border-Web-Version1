categories = [
    {'value': 'apparel', 'label': '服装配饰'},
    {'value': 'shoes', 'label': '鞋类箱包'},
    {'value': 'home', 'label': '家居用品'},
    {'value': 'electronics', 'label': '消费电子'},
]

markets = [
    {'value': 'US', 'label': '美国'},
    {'value': 'EU', 'label': '欧洲'},
    {'value': 'JP', 'label': '日本'},
    {'value': 'UK', 'label': '英国'},
]

mock_jobs = [
    {'id': '1001', 'type': 'trademark', 'title': 'ACTIVEWEAR 轻量运动鞋风险检测', 'brand': 'ACTIVEWEAR', 'category': 'shoes', 'market': 'US', 'status': 'done', 'riskLevel': 'high', 'riskScore': 85, 'createdAt': '2026-06-01 10:20', 'ownerName': '张三'},
    {'id': '1002', 'type': 'design', 'title': 'DZMZIVAWEBIA 家居灯具外观检测', 'brand': 'DZMZIVAWEBIA', 'category': 'home', 'market': 'EU', 'status': 'processing', 'riskLevel': 'pending', 'riskScore': None, 'createdAt': '2026-06-02 09:15', 'ownerName': '李四'},
    {'id': '1003', 'type': 'copyright', 'title': '动漫手机壳版权素材检测', 'brand': 'MOONCASE', 'category': 'electronics', 'market': 'JP', 'status': 'done', 'riskLevel': 'medium', 'riskScore': 56, 'createdAt': '2026-06-03 15:42', 'ownerName': '王五'},
    {'id': '1004', 'type': 'trademark', 'title': '自有品牌英文词商标预检', 'brand': 'NORTHBIRD', 'category': 'apparel', 'market': 'UK', 'status': 'done', 'riskLevel': 'low', 'riskScore': 24, 'createdAt': '2026-06-04 11:08', 'ownerName': '赵六'},
]

mock_reports = [
    {
        'id': 'r-1001',
        'jobId': '1001',
        'title': 'ACTIVEWEAR 轻量运动鞋知识产权风险报告',
        'generatedAt': '2026-06-01 10:26',
        'riskLevel': 'high',
        'riskScore': 85,
        'summary': '检测发现该商品在品牌词、鞋型轮廓和详情页素材中存在较高疑似侵权风险。主要命中 ACTIVEWEAR 近似文字商标、运动鞋外观专利和训练场景图片版权素材。',
        'categoryScores': [
            {'type': 'trademark', 'label': '商标', 'score': 89, 'hits': 3},
            {'type': 'design', 'label': '外观', 'score': 82, 'hits': 2},
            {'type': 'copyright', 'label': '版权', 'score': 71, 'hits': 1},
        ],
        'evidence': [
            {'id': 'ev-1', 'category': 'trademark', 'matched': 'ACTIVEWEAR', 'source': 'USPTO', 'similarity': 0.89, 'description': '品牌词与美国已注册运动服饰商标高度近似，且商品类目同属鞋服相关类别。', 'imageUrl': '/evidence/activewear.svg'},
            {'id': 'ev-2', 'category': 'design', 'matched': '运动鞋外观轮廓', 'source': 'Google Patents', 'similarity': 0.82, 'description': '鞋底齿纹、侧面线条和鞋头比例与目标市场公开外观专利存在明显相似。', 'imageUrl': '/evidence/shoe-design.svg'},
            {'id': 'ev-3', 'category': 'copyright', 'matched': '训练场景宣传图', 'source': 'Image Rights Index', 'similarity': 0.71, 'description': '详情页背景图与第三方素材库图片构图高度接近，建议替换为自有拍摄素材。', 'imageUrl': '/evidence/training-image.svg'},
        ],
        'suggestions': ['立即替换 ACTIVEWEAR 品牌词，避免与已注册商标造成混淆。', '调整鞋型侧面线条和鞋底纹路，再次进行外观复检。', '替换详情页训练场景图片，保留素材授权证明。', '进入目标市场销售前提交人工复核，确认剩余风险。'],
    }
]

admin_stats = {
    'totalJobs': 1286,
    'totalUsers': 342,
    'completedJobs': 1038,
    'highRiskRate': 0.31,
}
