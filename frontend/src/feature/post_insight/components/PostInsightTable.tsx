"use client";

import { PostInsightData } from "../types/postInsight";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Image from "next/image";
import { ExternalLink } from "lucide-react";

interface PostInsightTableProps {
  data: PostInsightData[];
}

export function PostInsightTable({ data }: PostInsightTableProps) {
  const formatNumber = (num: number): string => {
    return num.toLocaleString();
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "IMAGE":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "VIDEO":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300";
      case "CAROUSEL_ALBUM":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300";
      case "STORY":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
    }
  };

  const getTypeDisplayName = (type: string) => {
    switch (type) {
      case "IMAGE": return "画像";
      case "VIDEO": return "動画";
      case "CAROUSEL_ALBUM": return "カルーセル";
      case "STORY": return "ストーリー";
      default: return type;
    }
  };

  const getThumbnailUrl = (post: PostInsightData): string => {
    const placeholderSvg = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yNCAzNkMzMC42Mjc0IDM2IDM2IDMwLjYyNzQgMzYgMjRDMzYgMTcuMzcyNiAzMC42Mjc0IDEyIDI0IDEyQzE3LjM3MjYgMTIgMTIgMTcuMzcyNiAxMiAyNEMxMiAzMC42Mjc0IDE3LjM3MjYgMzYgMjQgMzZaIiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+CjxwYXRoIGQ9Ik0yOSAyMUM5LjE1IDIxIDkuMTUgMjcgMjkgMjciIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==';
    
    // 有効なURLかチェック
    const isValidUrl = (url: string): boolean => {
      if (!url || url.trim() === '') return false;
      if (url.startsWith('data:')) return true; // SVG data URL
      if (url.startsWith('http://example.com') || url.startsWith('https://example.com')) return false; // ダミーURL除外
      try {
        new URL(url);
        return true;
      } catch {
        return false;
      }
    };
    
    // 順番に確認してvalid URLを返す
    if (isValidUrl(post.thumbnail)) return post.thumbnail;
    if (isValidUrl(post.media_url)) return post.media_url;
    return placeholderSvg;
  };

  // 横軸に投稿、縦軸に要素のテーブル構造
  const rows = [
    {
      label: "投稿日",
      cells: data.map(post => formatDate(post.date))
    },
    {
      label: "サムネイル",
      cells: data.map(post => (
        <div key={post.id} className="relative w-12 h-12 rounded-md overflow-hidden mx-auto group">
          <Image
            src={getThumbnailUrl(post)}
            alt="投稿サムネイル"
            fill
            className="object-cover"
            sizes="48px"
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yNCAzNkMzMC42Mjc0IDM2IDM2IDMwLjYyNzQgMzYgMjRDMzYgMTcuMzcyNiAzMC42Mjc0IDEyIDI0IDEyQzE3LjM3MjYgMTIgMTIgMTcuMzcyNiAxMiAyNEMxMiAzMC42Mjc0IDE3LjM3MjYgMzYgMjQgMzZaIiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+CjxwYXRoIGQ9Ik0yOSAyMUM5LjE1IDIxIDkuMTUgMjcgMjkgMjciIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==';
            }}
          />
          {post.permalink && (
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
              <a 
                href={post.permalink} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-white hover:text-gray-200"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          )}
        </div>
      ))
    },
    {
      label: "タイプ",
      cells: data.map(post => (
        <Badge key={post.id} variant="secondary" className={getTypeColor(post.type)}>
          {getTypeDisplayName(post.type)}
        </Badge>
      ))
    },
    {
      label: "リーチ",
      cells: data.map(post => formatNumber(post.reach))
    },
    {
      label: "いいね",
      cells: data.map(post => formatNumber(post.likes))
    },
    {
      label: "コメント",
      cells: data.map(post => formatNumber(post.comments))
    },
    {
      label: "シェア",
      cells: data.map(post => formatNumber(post.shares))
    },
    {
      label: "保存",
      cells: data.map(post => formatNumber(post.saves))
    },
    {
      label: "EG率(%)",
      cells: data.map(post => (
        <span key={post.id} className={post.engagement_rate >= 8 ? "text-green-600" : 
                                     post.engagement_rate >= 5 ? "text-yellow-600" : "text-red-600"}>
          {post.engagement_rate}%
        </span>
      ))
    },
    {
      label: "視聴数",
      cells: data.map(post => 
        post.views > 0 ? formatNumber(post.views) : 
        <span key={post.id} className="text-muted-foreground">---</span>
      )
    },
    {
      label: "視聴率(%)",
      cells: data.map(post => (
        post.view_rate && post.view_rate > 0 ? (
          <span key={post.id} className={post.view_rate >= 70 ? "text-green-600" : 
                                       post.view_rate >= 50 ? "text-yellow-600" : "text-red-600"}>
            {post.view_rate}%
          </span>
        ) : (
          <span key={post.id} className="text-muted-foreground">---</span>
        )
      ))
    }
  ];

  return (
    <Card className="w-full">
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableBody>
              {rows.map((row, rowIndex) => (
                <TableRow key={rowIndex}>
                  <TableCell className="font-medium sticky left-0 bg-background border-r">
                    {row.label}
                  </TableCell>
                  {row.cells.map((cell, cellIndex) => (
                    <TableCell key={cellIndex} className="text-center">
                      {cell}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}