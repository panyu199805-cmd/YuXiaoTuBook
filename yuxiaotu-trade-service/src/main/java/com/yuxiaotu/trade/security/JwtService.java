package com.yuxiaotu.trade.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.yuxiaotu.trade.config.TradeProperties;
import org.springframework.stereotype.Component;

@Component
public class JwtService {
    private final Algorithm algorithm;

    public JwtService(TradeProperties properties) {
        this.algorithm = Algorithm.HMAC256(properties.getJwtSecret());
    }

    public Long parseUserId(String token) {
        DecodedJWT jwt = JWT.require(algorithm).build().verify(token);
        String subject = jwt.getSubject();
        if (subject == null || subject.isBlank()) {
            Object subClaim = jwt.getClaim("sub").as(Object.class);
            if (subClaim instanceof Number number) {
                return number.longValue();
            }
            if (subClaim != null) {
                return Long.parseLong(String.valueOf(subClaim));
            }
            throw new IllegalArgumentException("missing sub");
        }
        return Long.parseLong(subject);
    }
}
