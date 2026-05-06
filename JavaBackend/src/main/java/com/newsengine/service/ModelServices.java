package com.newsengine.service;
import com.newsengine.repository.InMemoryRepositories; import com.newsengine.schema.Models.*; import org.springframework.stereotype.Service; import java.time.Instant; import java.util.*; import java.util.stream.Collectors;
@Service public class ModelServices {
 private final InMemoryRepositories repo; public ModelServices(InMemoryRepositories r){this.repo=r;}
 public Optional<NewsItemSchema> getNewsById(String id){ return Optional.ofNullable(repo.news.get(id)); }
 public List<NewsItemSchema> listNews(int limit){ return repo.news.values().stream().limit(limit).toList(); }
 public boolean createNews(NewsItemSchema d){ return repo.news.putIfAbsent(d.newsId(),d)==null; }
 public Optional<UserSchema> getUserByEmail(String email){ return repo.users.values().stream().filter(u->u.email().equalsIgnoreCase(email)).findFirst(); }
 public Optional<UserSchema> getUserById(String id){ return Optional.ofNullable(repo.users.get(id)); }
 public boolean createUser(UserSchema u){ repo.users.put(u.userId(),u); return true; }
 public List<UserSchema> getByTenant(String t){ return repo.users.values().stream().filter(u->u.tenantId().equals(t)).toList(); }
 public Optional<TenantSchema> getTenantByEmail(String e){ return repo.tenants.values().stream().filter(t->t.email().equalsIgnoreCase(e)).findFirst(); }
 public Optional<TenantSchema> getTenantById(String id){ return Optional.ofNullable(repo.tenants.get(id)); }
 public boolean createTenant(TenantSchema t){ if(repo.tenants.containsKey(t.tenantId())) return false; repo.tenants.put(t.tenantId(),t); return true; }
 public Optional<InterestSchema> getInterestByUser(String uid){ return repo.interests.values().stream().filter(i->i.userId().equals(uid)).findFirst(); }
 public List<InterestSchema> allInterests(){ return new ArrayList<>(repo.interests.values()); }
 public boolean upsertInterest(String uid,List<String> kw,List<String> cat,String email){ var ex=getInterestByUser(uid); var i=new InterestSchema(ex.map(InterestSchema::interestId).orElse(UUID.randomUUID().toString()),uid,kw,cat,email); repo.interests.put(i.interestId(),i); return true; }
 public boolean createTrigger(TriggerSchema t){ repo.triggers.put(t.triggerId(),t); return true; }
 public List<TriggerSchema> getTriggersByUser(String uid){ return repo.triggers.values().stream().filter(t->t.userId().equals(uid)).sorted(Comparator.comparing(TriggerSchema::createdAt).reversed()).toList(); }
 public long unreadCount(String uid){ return repo.triggers.values().stream().filter(t->t.userId().equals(uid)&&!t.sent()).count(); }
 public void markRead(String id){ var t=repo.triggers.get(id); if(t!=null) repo.triggers.put(id,new TriggerSchema(t.triggerId(),t.userId(),t.newsId(),t.score(),true,t.createdAt())); }
 public boolean saveChat(ChatHistorySchema c){ repo.chats.put(c.chatId(),c); return true; }
 public List<ChatHistorySchema> chatsByUser(String uid){ return repo.chats.values().stream().filter(c->c.userId().equals(uid)).sorted(Comparator.comparing(ChatHistorySchema::createdAt)).collect(Collectors.toList()); }
}
