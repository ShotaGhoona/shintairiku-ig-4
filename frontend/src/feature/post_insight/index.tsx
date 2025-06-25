"use client";

import { useState } from "react";
import { format } from "date-fns";
import { Calendar as CalendarIcon, AlertCircle, Loader2 } from "lucide-react";
import { DateRange } from "react-day-picker";
import { PostInsightTable } from "./components/PostInsightTable";
import { PostInsightChart } from "./components/PostInsightChart";
import { usePostInsights } from "./hooks/usePostInsights";
import { useAccount } from "../../hooks/useAccount";
import { ContentType, contentTypes, MediaType } from "./types/postInsight";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

export default function PostInsight() {
  // デフォルトを先月に設定
  const getLastMonth = () => {
    const now = new Date();
    const firstDayOfLastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const lastDayOfLastMonth = new Date(now.getFullYear(), now.getMonth(), 0);
    return {
      from: firstDayOfLastMonth,
      to: lastDayOfLastMonth
    };
  };

  const [date, setDate] = useState<DateRange | undefined>(getLastMonth());
  const [selectedType, setSelectedType] = useState<ContentType>("All");

  // 選択されたアカウントを取得
  const { selectedAccount } = useAccount();

  // APIからデータを取得（期間フィルタなし）
  const {
    data: apiData,
    posts,
    loading,
    error,
    filterByMediaType,
    clearError,
    refresh
  } = usePostInsights({
    account_id: selectedAccount?.instagram_user_id || "", // 選択アカウントのInstagram User ID
    limit: 100 // 全データを取得
  }, {
    autoFetch: !!selectedAccount && !!selectedAccount.instagram_user_id, // アカウントとIDが両方存在する場合のみ自動取得
    cacheTime: 5 * 60 * 1000, // 5分キャッシュ
  });

  // フィルタリングされたデータ（フロントエンドで期間とタイプをフィルタ）
  const getFilteredData = () => {
    let filtered = posts;

    // メディアタイプフィルタ
    if (selectedType !== "All") {
      filtered = filterByMediaType(selectedType as MediaType);
    }

    // 日付フィルタ（フロントエンド側で実行）
    if (date?.from && date?.to) {
      filtered = filtered.filter(post => {
        const postDate = new Date(post.date);
        const fromDate = new Date(date.from!);
        const toDate = new Date(date.to!);
        
        // 時間を00:00:00に正規化
        fromDate.setHours(0, 0, 0, 0);
        toDate.setHours(23, 59, 59, 999);
        postDate.setHours(0, 0, 0, 0);
        
        return postDate >= fromDate && postDate <= toDate;
      });
    }

    return filtered;
  };

  const filteredData = getFilteredData();

  return (
    <div id="post-analysis-content" className="space-y-6 p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          {/* データソース表示 */}
          {apiData && (
            <p className="text-xs text-muted-foreground mt-1">
              @{apiData.meta.username} ({filteredData.length}件 / 全{apiData.meta.total_posts}件の投稿)
            </p>
          )}
        </div>
        
        {/* フィルター */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          {/* 日付範囲選択 */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">期間:</span>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  id="date"
                  variant="outline"
                  className={cn(
                    "w-[300px] justify-start text-left font-normal",
                    !date && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date?.from ? (
                    date.to ? (
                      <>
                        {format(date.from, "yyyy/MM/dd")} -{" "}
                        {format(date.to, "yyyy/MM/dd")}
                      </>
                    ) : (
                      format(date.from, "yyyy/MM/dd")
                    )
                  ) : (
                    <span>日付を選択してください</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  initialFocus
                  mode="range"
                  defaultMonth={date?.from}
                  selected={date}
                  onSelect={setDate}
                  numberOfMonths={2}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* コンテンツタイプ選択 */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">タイプ:</span>
            <Tabs
              value={selectedType}
              onValueChange={(value) => setSelectedType(value as ContentType)}
              className="w-auto"
            >
              <TabsList className="grid w-full grid-cols-5">
                {contentTypes.map((type) => (
                  <TabsTrigger key={type} value={type} className="text-xs">
                    {type}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>
        </div>
      </div>

      {/* エラー表示 */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex justify-between items-center">
            <span>{error}</span>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearError}
              >
                閉じる
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={refresh}
                disabled={loading}
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                再試行
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* データ表示 */}
      <div className="space-y-6">
        {!selectedAccount ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-center text-muted-foreground">
              <p>アカウントを選択してください</p>
              <p className="text-sm mt-1">ヘッダーからInstagramアカウントを選択してください</p>
            </div>
          </div>
        ) : loading && !posts.length ? (
          <div className="flex items-center justify-center h-32">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" />
              投稿データを読み込み中...
            </div>
          </div>
        ) : filteredData.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-center text-muted-foreground">
              <p>選択した条件に一致する投稿がありません</p>
              <p className="text-sm mt-1">日付範囲またはメディアタイプを変更してください</p>
            </div>
          </div>
        ) : (
          <>
            {/* テーブル */}
            <PostInsightTable data={filteredData} />
            
            {/* グラフ */}
            <PostInsightChart data={filteredData} />
          </>
        )}
      </div>
    </div>
  );
}