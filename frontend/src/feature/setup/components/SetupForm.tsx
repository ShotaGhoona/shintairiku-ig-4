"use client";

import { useState } from "react";
import { Loader2, Eye, EyeOff, CheckCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { SetupFormData, SetupFormErrors, SetupStatus } from "../types/setup";

interface SetupFormProps {
  onSubmit: (data: SetupFormData) => Promise<void>;
  status: SetupStatus;
  errors: SetupFormErrors;
}

export function SetupForm({ onSubmit, status, errors }: SetupFormProps) {
  const [formData, setFormData] = useState<SetupFormData>({
    app_id: "",
    app_secret: "",
    short_token: "",
  });

  const [showSecret, setShowSecret] = useState(false);
  const [showToken, setShowToken] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  const handleInputChange = (field: keyof SetupFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const isLoading = status === 'loading';
  const isFormValid = formData.app_id && formData.app_secret && formData.short_token;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          📝 アカウント登録
        </CardTitle>
        <CardDescription>
          Instagram App ID、App Secret、短期トークンを入力してアカウントを自動登録します
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* App ID */}
          <div className="space-y-2">
            <Label htmlFor="app_id">Instagram App ID</Label>
            <Input
              id="app_id"
              type="text"
              placeholder="1234567890123456"
              value={formData.app_id}
              onChange={(e) => handleInputChange("app_id", e.target.value)}
              disabled={isLoading}
              className={errors.app_id ? "border-red-500" : ""}
            />
            {errors.app_id && (
              <p className="text-sm text-red-500">{errors.app_id}</p>
            )}
          </div>

          {/* App Secret */}
          <div className="space-y-2">
            <Label htmlFor="app_secret">Instagram App Secret</Label>
            <div className="relative">
              <Input
                id="app_secret"
                type={showSecret ? "text" : "password"}
                placeholder="abcdef1234567890abcdef1234567890"
                value={formData.app_secret}
                onChange={(e) => handleInputChange("app_secret", e.target.value)}
                disabled={isLoading}
                className={errors.app_secret ? "border-red-500" : ""}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowSecret(!showSecret)}
                disabled={isLoading}
              >
                {showSecret ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            {errors.app_secret && (
              <p className="text-sm text-red-500">{errors.app_secret}</p>
            )}
          </div>

          {/* Short Token */}
          <div className="space-y-2">
            <Label htmlFor="short_token">Instagram Short Token</Label>
            <div className="relative">
              <Textarea
                id="short_token"
                placeholder="EAARrfZCwPTGU..."
                value={formData.short_token}
                onChange={(e) => handleInputChange("short_token", e.target.value)}
                disabled={isLoading}
                className={`min-h-[80px] resize-none ${errors.short_token ? "border-red-500" : ""}`}
                style={{ fontFamily: 'monospace', fontSize: '12px' }}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-2 top-2 h-6 w-6 p-0 hover:bg-transparent"
                onClick={() => setShowToken(!showToken)}
                disabled={isLoading}
              >
                {showToken ? (
                  <EyeOff className="h-3 w-3" />
                ) : (
                  <Eye className="h-3 w-3" />
                )}
              </Button>
            </div>
            {errors.short_token && (
              <p className="text-sm text-red-500">{errors.short_token}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Facebook Graph API Explorerで取得した短期アクセストークンを入力してください
            </p>
          </div>

          {/* エラーメッセージ */}
          {errors.general && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errors.general}</AlertDescription>
            </Alert>
          )}

          {/* 成功メッセージ */}
          {status === 'success' && (
            <Alert className="border-green-500 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700">
                アカウントのセットアップが完了しました！
              </AlertDescription>
            </Alert>
          )}

          {/* 送信ボタン */}
          <Button
            type="submit"
            disabled={!isFormValid || isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                アカウントを取得中...
              </>
            ) : (
              <>
                🚀 アカウント取得
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}