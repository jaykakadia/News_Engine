package com.newsengine.controller;
import com.newsengine.schema.Models.*; import com.newsengine.service.ModelServices; import org.springframework.web.bind.annotation.*; import java.time.Instant; import java.util.*;
@RestController @RequestMapping("/auth") public class AuthController {
 private final ModelServices models; public AuthController(ModelServices m){this.models=m;}
 @PostMapping("/register/agency") public Map<String,Object> registerAgency(@RequestBody Map<String,String> req){ var id=UUID.randomUUID().toString(); boolean ok=models.createTenant(new TenantSchema(id,req.get("name"),req.get("email"),req.getOrDefault("password",""),Instant.now())); return Map.of("success",ok,"tenant_id",id); }
 @PostMapping("/register/user") public Map<String,Object> registerUser(@RequestBody Map<String,String> req){ var id=UUID.randomUUID().toString(); boolean ok=models.createUser(new UserSchema(id,req.get("tenant_id"),req.get("email"),req.get("name"),req.getOrDefault("password",""),"user",Instant.now())); return Map.of("success",ok,"user_id",id); }
}
