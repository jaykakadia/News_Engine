package com.newsengine.controller;
import com.newsengine.schema.Models.ChatHistorySchema; import com.newsengine.service.ModelServices; import org.springframework.web.bind.annotation.*; import java.time.Instant; import java.util.*;
@RestController @RequestMapping("/api/chat") public class ChatController {
 private final ModelServices models; public ChatController(ModelServices m){this.models=m;}
 @GetMapping("/history/{userId}") public Map<String,Object> history(@PathVariable String userId){ return Map.of("history",models.chatsByUser(userId)); }
 @PostMapping public Map<String,Object> apiChat(@RequestBody Map<String,Object> req){ String q=(String)req.getOrDefault("query",""); String user=(String)req.getOrDefault("user_id",""); String answer="Stub response: integrate Gemini + Chroma retrieval here."; if(!user.isBlank()) models.saveChat(new ChatHistorySchema(UUID.randomUUID().toString(),user,q,answer,Instant.now())); return Map.of("response",answer); }
}
