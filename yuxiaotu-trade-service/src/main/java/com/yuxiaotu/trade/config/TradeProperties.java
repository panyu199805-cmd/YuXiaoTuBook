package com.yuxiaotu.trade.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "trade")
public class TradeProperties {
    private String jwtSecret = "dev-secret";
    private boolean mockPayEnabled = true;
    private boolean memberMockPayEnabled = true;
    private String paymentProvider = "mock";
    private int orderTimeoutMinutes = 30;

    public String getJwtSecret() {
        if (jwtSecret == null || jwtSecret.isBlank()) {
            return "yuxiaotu-dev-secret-key-32chars-min";
        }
        return jwtSecret.trim();
    }

    public void setJwtSecret(String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }

    public boolean isMockPayEnabled() {
        return mockPayEnabled;
    }

    public void setMockPayEnabled(boolean mockPayEnabled) {
        this.mockPayEnabled = mockPayEnabled;
    }

    public boolean isMemberMockPayEnabled() {
        return memberMockPayEnabled;
    }

    public void setMemberMockPayEnabled(boolean memberMockPayEnabled) {
        this.memberMockPayEnabled = memberMockPayEnabled;
    }

    public String getPaymentProvider() {
        return paymentProvider;
    }

    public void setPaymentProvider(String paymentProvider) {
        this.paymentProvider = paymentProvider;
    }

    public int getOrderTimeoutMinutes() {
        return orderTimeoutMinutes;
    }

    public void setOrderTimeoutMinutes(int orderTimeoutMinutes) {
        this.orderTimeoutMinutes = orderTimeoutMinutes;
    }
}
