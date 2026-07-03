package com.yuxiaotu.trade.dto.request;

import jakarta.validation.constraints.NotNull;

public class SubscribeRequest {
    @NotNull
    private Long packageId;

    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
}
