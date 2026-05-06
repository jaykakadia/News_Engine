package com.newsengine.controller;
import com.newsengine.ingestion.RssIngestorService; import com.newsengine.service.ModelServices; import org.springframework.web.bind.annotation.*; import java.util.*;
@RestController @RequestMapping("/api/news") public class NewsController {
 private final ModelServices models; private final RssIngestorService ingestor;
 public NewsController(ModelServices m,RssIngestorService i){models=m;ingestor=i;}
 @GetMapping public Object getNews(){ return models.listNews(200); }
 @PostMapping("/ingest") public Map<String,Object> ingest(@RequestBody Map<String,String> req){ boolean ok=ingestor.storeArticle(req.getOrDefault("title",""),req.getOrDefault("link",""),req.getOrDefault("summary",""),req.getOrDefault("category","General")); return Map.of("ingested",ok); }
}
