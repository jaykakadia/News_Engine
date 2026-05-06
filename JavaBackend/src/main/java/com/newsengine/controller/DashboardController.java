package com.newsengine.controller;
import com.newsengine.service.ModelServices; import org.springframework.web.bind.annotation.*; import java.util.*;
@RestController public class DashboardController { private final ModelServices models; public DashboardController(ModelServices m){this.models=m;} 
 @GetMapping("/") public Object index(){ return models.listNews(50); }
 @GetMapping("/article/{newsId}") public Object article(@PathVariable String newsId){ return models.getNewsById(newsId).orElse(Map.of("error","not found")); }
}
