package com.yuxiaotu.trade.dto.response;

import java.util.List;
import java.util.Map;

public class OrderVO {
    private Long id;
    private String orderNo;
    private Double totalAmount;
    private String status;
    private String statusLabel;
    private String receiverName;
    private String receiverPhone;
    private String receiverAddress;
    private String payTime;
    private String createdAt;
    private List<Map<String, Object>> items;
    private String shipCompany;
    private String shipTrackingNo;
    private String shippedAt;
    private String completedAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getOrderNo() { return orderNo; }
    public void setOrderNo(String orderNo) { this.orderNo = orderNo; }
    public Double getTotalAmount() { return totalAmount; }
    public void setTotalAmount(Double totalAmount) { this.totalAmount = totalAmount; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getStatusLabel() { return statusLabel; }
    public void setStatusLabel(String statusLabel) { this.statusLabel = statusLabel; }
    public String getReceiverName() { return receiverName; }
    public void setReceiverName(String receiverName) { this.receiverName = receiverName; }
    public String getReceiverPhone() { return receiverPhone; }
    public void setReceiverPhone(String receiverPhone) { this.receiverPhone = receiverPhone; }
    public String getReceiverAddress() { return receiverAddress; }
    public void setReceiverAddress(String receiverAddress) { this.receiverAddress = receiverAddress; }
    public String getPayTime() { return payTime; }
    public void setPayTime(String payTime) { this.payTime = payTime; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public List<Map<String, Object>> getItems() { return items; }
    public void setItems(List<Map<String, Object>> items) { this.items = items; }
    public String getShipCompany() { return shipCompany; }
    public void setShipCompany(String shipCompany) { this.shipCompany = shipCompany; }
    public String getShipTrackingNo() { return shipTrackingNo; }
    public void setShipTrackingNo(String shipTrackingNo) { this.shipTrackingNo = shipTrackingNo; }
    public String getShippedAt() { return shippedAt; }
    public void setShippedAt(String shippedAt) { this.shippedAt = shippedAt; }
    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }
}
