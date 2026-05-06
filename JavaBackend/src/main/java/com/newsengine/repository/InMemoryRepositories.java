package com.newsengine.repository;
import com.newsengine.schema.Models.*; import org.springframework.stereotype.Repository; import java.util.*; import java.util.concurrent.*;
@Repository public class InMemoryRepositories {
 public final Map<String,NewsItemSchema> news=new ConcurrentHashMap<>();
 public final Map<String,UserSchema> users=new ConcurrentHashMap<>();
 public final Map<String,TenantSchema> tenants=new ConcurrentHashMap<>();
 public final Map<String,InterestSchema> interests=new ConcurrentHashMap<>();
 public final Map<String,TriggerSchema> triggers=new ConcurrentHashMap<>();
 public final Map<String,ChatHistorySchema> chats=new ConcurrentHashMap<>();
}
