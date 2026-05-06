package com.newsengine.ingestion;
import com.newsengine.schema.Models.*; import com.newsengine.service.ModelServices; import org.springframework.stereotype.Service; import java.time.Instant; import java.util.*;
@Service public class TriggerEngineService {
 private final ModelServices models; public TriggerEngineService(ModelServices m){this.models=m;}
 public int scoreArticle(NewsItemSchema n, InterestSchema i){ int s=0; var t=n.title().toLowerCase(); var c=n.content()==null?"":n.content().toLowerCase(); for(var kw:i.keywords()){ var k=kw.toLowerCase().trim(); if(k.isEmpty()) continue; if(t.contains(k)) s+=30; if(c.contains(k)) s+=30;} for(var cat:i.categories()){ if(cat.trim().equalsIgnoreCase(n.category().trim())) {s+=20;break;}} return Math.min(s,100);} 
 public int checkTriggers(NewsItemSchema news){ int created=0; for(var interest:models.allInterests()){ boolean cat=interest.categories().stream().anyMatch(c->c.equalsIgnoreCase(news.category())); int score=scoreArticle(news,interest); if(cat){ models.createTrigger(new TriggerSchema(UUID.randomUUID().toString(),interest.userId(),news.newsId(),score,false,Instant.now())); created++; }} return created; }
}
