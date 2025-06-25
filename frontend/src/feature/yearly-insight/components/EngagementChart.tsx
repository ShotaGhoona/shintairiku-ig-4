"use client";

import { MonthlyAnalytics } from "../dummy-data/dummy-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface EngagementChartProps {
  data: MonthlyAnalytics[];
}

export function EngagementChart({ data }: EngagementChartProps) {
  const chartData = data.map((item) => ({
    month: item.month,
    いいね: item.likes,
    コメント: item.comments,
    保存: item.saves,
    シェア: item.shares,
    インプレッション: item.impressions,
  }));

  const formatTooltipValue = (value: number, name: string) => {
    return [value.toLocaleString(), name];
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">エンゲージメント分析</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="month" 
                className="text-sm"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                yAxisId="left" 
                className="text-sm"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => value.toLocaleString()}
              />
              <YAxis 
                yAxisId="right" 
                orientation="right" 
                className="text-sm"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={formatTooltipValue}
                labelClassName="text-foreground"
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  borderColor: "hsl(var(--border))",
                  borderRadius: "6px",
                }}
              />
              <Legend />
              
              {/* 積み上げ棒グラフ */}
              <Bar 
                yAxisId="left" 
                dataKey="いいね" 
                stackId="engagement" 
                fill="#ffb6c1" 
                radius={[0, 0, 0, 0]}
              />
              <Bar 
                yAxisId="left" 
                dataKey="コメント" 
                stackId="engagement" 
                fill="#add8e6" 
                radius={[0, 0, 0, 0]}
              />
              <Bar 
                yAxisId="left" 
                dataKey="保存" 
                stackId="engagement" 
                fill="#98fb98" 
                radius={[0, 0, 0, 0]}
              />
              <Bar 
                yAxisId="left" 
                dataKey="シェア" 
                stackId="engagement" 
                fill="#ffdab9" 
                radius={[2, 2, 0, 0]}
              />
              
              {/* 折線グラフ */}
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="インプレッション"
                stroke="hsl(var(--primary))"
                strokeWidth={3}
                dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: "hsl(var(--primary))" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}