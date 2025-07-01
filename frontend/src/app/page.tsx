"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  BarChart3, 
  Calendar, 
  Image as ImageIcon,
  ArrowRight
} from "lucide-react";

export default function Home() {
  const features = [
    {
      icon: Calendar,
      title: "年間分析",
      description: "月ごとの成長トレンドとエンゲージメント分析",
      href: "/yearly-insight",
      color: "text-blue-600"
    },
    {
      icon: BarChart3,
      title: "月間分析", 
      description: "日別のパフォーマンスと詳細メトリクス",
      href: "/monthly-insight",
      color: "text-green-600"
    },
    {
      icon: ImageIcon,
      title: "投稿分析",
      description: "個別投稿のエンゲージメントと効果測定",
      href: "/post_insight",
      color: "text-purple-600"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-6xl mx-auto">

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="border-gray-200 hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <feature.icon className={`w-10 h-10 ${feature.color} mb-4`} />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {feature.description}
                  </p>
                  <Button asChild variant="outline" className="w-full">
                    <Link href={feature.href}>
                      詳細を見る
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Trust Indicators */}
          <div className="text-center mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-4">
              ✨ プロフェッショナルなInstagramアナリティクス
            </p>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-600">
              <span>📊 リアルタイム分析</span>
              <span>📈 成長トレンド</span>
              <span>📋 PDF レポート</span>
              <span>🔒 安全な接続</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}