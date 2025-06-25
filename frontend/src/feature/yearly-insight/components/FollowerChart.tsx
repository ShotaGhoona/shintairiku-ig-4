"use client";

import { MonthlyAnalytics } from "../dummy-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface FollowerChartProps {
  data: MonthlyAnalytics[];
}

export function FollowerChart({ data }: FollowerChartProps) {
  const chartData = data.map((item) => ({
    month: item.month,
    フォロワー数: item.follower_count,
    フォロー数: item.following_count,
  }));

  const formatTooltipValue = (value: number | null, name: string) => {
    if (value === null) return ["---", name];
    return [value.toLocaleString(), name];
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">フォロワー/フォロー数推移</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
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
                className="text-sm"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => value.toLocaleString()}
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
              <Line
                type="monotone"
                dataKey="フォロワー数"
                stroke="hsl(var(--primary))"
                strokeWidth={3}
                dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: "hsl(var(--primary))" }}
              />
              <Line
                type="monotone"
                dataKey="フォロー数"
                stroke="hsl(var(--secondary))"
                strokeWidth={2}
                strokeDasharray="8 4"
                dot={{ fill: "hsl(var(--secondary))", strokeWidth: 2, r: 3 }}
                activeDot={{ r: 5, fill: "hsl(var(--secondary))" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}