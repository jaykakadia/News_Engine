package com.newsengine.config;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import java.util.List;
@Configuration
public class AppConfig {
 @Value("${news.rss-feeds:https://news.google.com/rss|General,https://techcrunch.com/feed/|Technology}")
 private String feeds;
 public List<String> getRssFeeds(){ return List.of(feeds.split(",")); }
}
