package com.drrr.bot;

import android.util.Log;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import okhttp3.*;

public class DRRRClient {
    private static final String TAG = "DRRRClient";
    
    private OkHttpClient client;
    private String baseUrl = "https://drrr.com";
    private String cookie;
    
    public DRRRClient() {
        // 初始化OkHttpClient
        client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
    }
    
    /**
     * 设置Cookie
     * @param cookie Cookie字符串
     */
    public void setCookie(String cookie) {
        this.cookie = cookie;
    }
    
    /**
     * 获取房间信息
     * @param roomId 房间ID
     * @param callback 回调接口
     */
    public void getRoomInfo(String roomId, DRRRResponseCallback callback) {
        String url = baseUrl + "/room/?id=" + roomId + "&api=json";
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36")
                .addHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
                .addHeader("Accept-Language", "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7")
                .addHeader("Accept-Encoding", "gzip, deflate")
                .addHeader("Connection", "keep-alive")
                .addHeader("Cookie", cookie != null ? cookie : "")
                .build();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Failed to get room info", e);
                if (callback != null) {
                    callback.onFailure(e.getMessage());
                }
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful() && response.body() != null) {
                    String responseBody = response.body().string();
                    Log.d(TAG, "Room info response: " + responseBody);
                    if (callback != null) {
                        callback.onSuccess(responseBody);
                    }
                } else {
                    Log.e(TAG, "Failed to get room info, code: " + response.code());
                    if (callback != null) {
                        callback.onFailure("HTTP " + response.code());
                    }
                }
            }
        });
    }
    
    /**
     * 加入房间
     * @param roomId 房间ID
     * @param callback 回调接口
     */
    public void joinRoom(String roomId, DRRRResponseCallback callback) {
        String url = baseUrl + "/room/?id=" + roomId;
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36")
                .addHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
                .addHeader("Accept-Language", "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7")
                .addHeader("Accept-Encoding", "gzip, deflate")
                .addHeader("Connection", "keep-alive")
                .addHeader("Cookie", cookie != null ? cookie : "")
                .build();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Failed to join room", e);
                if (callback != null) {
                    callback.onFailure(e.getMessage());
                }
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    Log.d(TAG, "Joined room successfully");
                    if (callback != null) {
                        callback.onSuccess("Joined room successfully");
                    }
                } else {
                    Log.e(TAG, "Failed to join room, code: " + response.code());
                    if (callback != null) {
                        callback.onFailure("HTTP " + response.code());
                    }
                }
            }
        });
    }
    
    /**
     * 发送消息
     * @param roomId 房间ID
     * @param message 消息内容
     * @param callback 回调接口
     */
    public void sendMessage(String roomId, String message, DRRRResponseCallback callback) {
        String url = baseUrl + "/room/?ajax=1";
        
        // 构造请求体
        RequestBody requestBody = new FormBody.Builder()
                .add("message", message)
                .add("id", roomId)
                .build();
        
        Request request = new Request.Builder()
                .url(url)
                .post(requestBody)
                .addHeader("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36")
                .addHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
                .addHeader("Accept-Language", "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7")
                .addHeader("Accept-Encoding", "gzip, deflate")
                .addHeader("Connection", "keep-alive")
                .addHeader("Cookie", cookie != null ? cookie : "")
                .build();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Failed to send message", e);
                if (callback != null) {
                    callback.onFailure(e.getMessage());
                }
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    Log.d(TAG, "Message sent successfully");
                    if (callback != null) {
                        callback.onSuccess("Message sent successfully");
                    }
                } else {
                    Log.e(TAG, "Failed to send message, code: " + response.code());
                    if (callback != null) {
                        callback.onFailure("HTTP " + response.code());
                    }
                }
            }
        });
    }
    
    /**
     * DRRR API响应回调接口
     */
    public interface DRRRResponseCallback {
        void onSuccess(String response);
        void onFailure(String error);
    }
}