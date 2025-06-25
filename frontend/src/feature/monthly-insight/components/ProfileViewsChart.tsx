"use client";

import { DailyAnalytics } from "../dummy-data/dummy-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ProfileViewsChartProps {
  data: DailyAnalytics[];
}

export function ProfileViewsChart({ data }: ProfileViewsChartProps) {
  const chartData = data.map((item) => ({
    date: `${item.date}日`,
    プロフィールアクセス数: item.profile_views,
  }));

  const formatTooltipValue = (value: number, name: string) => {
    return [value.toLocaleString(), name];
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold">プロフィールアクセス数推移</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{
                top: 10,
                right: 10,
                left: 0,
                bottom: 0,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="date" 
                className="text-xs"
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
              />
              <YAxis 
                className="text-xs"
                tick={{ fontSize: 10 }}
                width={30}
              />
              <Tooltip
                formatter={formatTooltipValue}
                labelClassName="text-foreground"
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  borderColor: "hsl(var(--border))",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
              />
              <Line
                type="monotone"
                dataKey="プロフィールアクセス数"
                stroke="#bfe5bf"
                strokeWidth={2}
                dot={{ fill: "#bfe5bf", strokeWidth: 1, r: 2 }}
                activeDot={{ r: 4, fill: "#bfe5bf" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}