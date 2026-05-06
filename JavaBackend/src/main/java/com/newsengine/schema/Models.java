package com.newsengine.schema;
import java.time.Instant; import java.util.*;
public class Models {
 public record TenantSchema(String tenantId,String name,String email,String passwordHash,Instant createdAt){}
 public record UserSchema(String userId,String tenantId,String email,String name,String passwordHash,String role,Instant createdAt){}
 public record InterestSchema(String interestId,String userId,List<String> keywords,List<String> categories,String alertEmail){}
 public record NewsItemSchema(String newsId,String title,String content,String source,String link,Instant publishedAt,String category,String embeddingId,Map<String,Object> entities){}
 public record TriggerSchema(String triggerId,String userId,String newsId,int score,boolean sent,Instant createdAt){}
 public record ChatHistorySchema(String chatId,String userId,String query,String response,Instant createdAt){}
}
