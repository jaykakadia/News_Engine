package com.newsengine.ingestion;
import com.newsengine.schema.Models.NewsItemSchema; import com.newsengine.service.ModelServices; import org.jsoup.Jsoup; import org.springframework.stereotype.Service; import java.security.*; import java.time.Instant; import java.util.*;
@Service public class RssIngestorService {
 private final ModelServices models; private final TriggerEngineService triggers; public RssIngestorService(ModelServices m,TriggerEngineService t){models=m;triggers=t;}
 public String generateId(String link,String title,String summary){ try{ var md=MessageDigest.getInstance("MD5"); var data=(link!=null&&!link.isBlank()?link:(title+"|"+summary)).toLowerCase(Locale.ROOT); byte[] d=md.digest(data.getBytes()); StringBuilder sb=new StringBuilder(); for(byte b:d) sb.append(String.format("%02x",b)); return sb.toString(); }catch(Exception e){ return UUID.randomUUID().toString(); }}
 public String fetchFullContent(String url){ try{return Jsoup.connect(url).userAgent("Mozilla/5.0").get().text();}catch(Exception e){return "";} }
 public int ingestRss(String feedUrl,String category){ return 0; }
 public boolean storeArticle(String title,String link,String summary,String category){ String id=generateId(link,title,summary); if(models.getNewsById(id).isPresent()) return false; String content=fetchFullContent(link); if(content.isBlank()) content=summary; var item=new NewsItemSchema(id,title,content,"Source",link,Instant.now(),category,id,Map.of()); models.createNews(item); triggers.checkTriggers(item); return true; }
}
