package com.newsengine.controller;
import com.newsengine.service.ModelServices; import org.springframework.web.bind.annotation.*; import java.util.*;
@RestController public class AlertsController {
 private final ModelServices models; public AlertsController(ModelServices m){this.models=m;}
 @GetMapping("/alerts/{userId}") public Object alerts(@PathVariable String userId){ return models.getTriggersByUser(userId); }
 @PostMapping("/alerts/read/{triggerId}") public Map<String,Object> markRead(@PathVariable String triggerId){ models.markRead(triggerId); return Map.of("success",true); }
 @PostMapping("/interests/{userId}") public Map<String,Object> saveInterests(@PathVariable String userId,@RequestBody Map<String,Object> req){ var kw=(List<String>)req.getOrDefault("keywords",List.of()); var cat=(List<String>)req.getOrDefault("categories",List.of()); var email=(String)req.getOrDefault("alert_email",null); return Map.of("success",models.upsertInterest(userId,kw,cat,email)); }
}
