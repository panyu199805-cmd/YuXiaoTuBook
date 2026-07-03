package com.yuxiaotu.trade.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.LocalDateTime;

@TableName("member_package")
public class MemberPackageEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String packageName;
    private Double price;
    private Integer validDay;
    private String rights;
    private Integer status;
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getPackageName() { return packageName; }
    public void setPackageName(String packageName) { this.packageName = packageName; }
    public Double getPrice() { return price; }
    public void setPrice(Double price) { this.price = price; }
    public Integer getValidDay() { return validDay; }
    public void setValidDay(Integer validDay) { this.validDay = validDay; }
    public String getRights() { return rights; }
    public void setRights(String rights) { this.rights = rights; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
