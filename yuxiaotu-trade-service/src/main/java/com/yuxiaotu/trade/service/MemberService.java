package com.yuxiaotu.trade.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.yuxiaotu.trade.common.BizException;
import com.yuxiaotu.trade.config.TradeProperties;
import com.yuxiaotu.trade.dto.request.SubscribeRequest;
import com.yuxiaotu.trade.entity.MemberOrderEntity;
import com.yuxiaotu.trade.entity.MemberPackageEntity;
import com.yuxiaotu.trade.entity.UserMemberEntity;
import com.yuxiaotu.trade.mapper.MemberOrderMapper;
import com.yuxiaotu.trade.mapper.MemberPackageMapper;
import com.yuxiaotu.trade.mapper.UserMemberMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class MemberService {
    private static final DateTimeFormatter ORDER_NO_TIME = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");
    private static final ObjectMapper MAPPER = new ObjectMapper();

    private final MemberPackageMapper packageMapper;
    private final MemberOrderMapper memberOrderMapper;
    private final UserMemberMapper userMemberMapper;
    private final TradeProperties properties;

    public MemberService(MemberPackageMapper packageMapper, MemberOrderMapper memberOrderMapper,
                         UserMemberMapper userMemberMapper, TradeProperties properties) {
        this.packageMapper = packageMapper;
        this.memberOrderMapper = memberOrderMapper;
        this.userMemberMapper = userMemberMapper;
        this.properties = properties;
    }

    public List<Map<String, Object>> listPackages() {
        List<MemberPackageEntity> packages = packageMapper.selectList(
                new LambdaQueryWrapper<MemberPackageEntity>()
                        .eq(MemberPackageEntity::getStatus, 1)
                        .orderByAsc(MemberPackageEntity::getPrice)
        );
        return packages.stream().map(pkg -> {
            Map<String, Object> row = new HashMap<>();
            row.put("id", pkg.getId());
            row.put("package_name", pkg.getPackageName());
            row.put("price", pkg.getPrice());
            row.put("valid_day", pkg.getValidDay());
            row.put("rights", parseRights(pkg.getRights()));
            return row;
        }).collect(Collectors.toList());
    }

    public Map<String, Object> getStatus(Long userId) {
        refreshVipIfExpired(userId);
        UserMemberEntity record = userMemberMapper.selectOne(
                new LambdaQueryWrapper<UserMemberEntity>().eq(UserMemberEntity::getUserId, userId)
        );
        if (record == null) {
            Map<String, Object> empty = new HashMap<>();
            empty.put("is_vip", false);
            empty.put("expire_time", null);
            empty.put("package_id", null);
            empty.put("package_name", null);
            return empty;
        }
        MemberPackageEntity pkg = packageMapper.selectById(record.getPackageId());
        Map<String, Object> profile = new HashMap<>();
        profile.put("is_vip", Boolean.TRUE.equals(record.getIsVip()));
        profile.put("expire_time", record.getExpireTime() == null ? null : record.getExpireTime().toString());
        profile.put("package_id", record.getPackageId());
        profile.put("package_name", pkg == null ? null : pkg.getPackageName());
        return profile;
    }

    @Transactional
    public Map<String, Object> subscribe(Long userId, SubscribeRequest req) {
        MemberPackageEntity pkg = packageMapper.selectOne(
                new LambdaQueryWrapper<MemberPackageEntity>()
                        .eq(MemberPackageEntity::getId, req.getPackageId())
                        .eq(MemberPackageEntity::getStatus, 1)
        );
        if (pkg == null) {
            throw new BizException(400, "套餐不存在或已下架");
        }
        MemberOrderEntity order = new MemberOrderEntity();
        order.setOrderNo("M" + LocalDateTime.now().format(ORDER_NO_TIME) + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        order.setUserId(userId);
        order.setPackageId(pkg.getId());
        order.setAmount(pkg.getPrice());
        order.setStatus("pending_payment");
        order.setPayChannel(properties.getPaymentProvider());
        order.setCreatedAt(LocalDateTime.now());
        order.setUpdatedAt(LocalDateTime.now());
        memberOrderMapper.insert(order);

        Map<String, Object> data = new HashMap<>();
        data.put("id", order.getId());
        data.put("order_no", order.getOrderNo());
        data.put("amount", order.getAmount());
        data.put("status", order.getStatus());
        return data;
    }

    @Transactional
    public Map<String, Object> mockPay(Long userId, Long orderId) {
        if (!properties.isMemberMockPayEnabled()) {
            throw new BizException(400, "模拟支付未开启");
        }
        MemberOrderEntity order = memberOrderMapper.selectOne(
                new LambdaQueryWrapper<MemberOrderEntity>()
                        .eq(MemberOrderEntity::getId, orderId)
                        .eq(MemberOrderEntity::getUserId, userId)
        );
        if (order == null) {
            throw new BizException(404, "订单不存在");
        }
        if (!"pending_payment".equals(order.getStatus())) {
            throw new BizException(400, "订单状态不允许支付");
        }
        order.setStatus("paid");
        order.setPayTime(LocalDateTime.now());
        order.setPayChannel("mock");
        order.setUpdatedAt(LocalDateTime.now());
        memberOrderMapper.updateById(order);

        UserMemberEntity member = activateMember(userId, order.getPackageId());
        Map<String, Object> profile = getStatus(userId);
        Map<String, Object> data = new HashMap<>();
        data.put("order_id", order.getId());
        data.put("member", profile);
        data.put("expire_time", member.getExpireTime() == null ? null : member.getExpireTime().toString());
        return data;
    }

    public void assertRealPaymentAvailable() {
        if ("mock".equalsIgnoreCase(properties.getPaymentProvider())) {
            throw new BizException(501, "真实支付尚未配置，请使用 mock-pay");
        }
        throw new BizException(501, "真实支付尚未配置");
    }

    private UserMemberEntity activateMember(Long userId, Long packageId) {
        MemberPackageEntity pkg = packageMapper.selectById(packageId);
        if (pkg == null) {
            throw new BizException(400, "套餐不存在");
        }
        LocalDateTime now = LocalDateTime.now();
        UserMemberEntity record = userMemberMapper.selectOne(
                new LambdaQueryWrapper<UserMemberEntity>().eq(UserMemberEntity::getUserId, userId)
        );
        LocalDateTime base = now;
        if (record != null && record.getExpireTime() != null && record.getExpireTime().isAfter(now)) {
            base = record.getExpireTime();
        }
        LocalDateTime expire = base.plusDays(pkg.getValidDay());
        if (record == null) {
            record = new UserMemberEntity();
            record.setUserId(userId);
            record.setPackageId(pkg.getId());
            record.setExpireTime(expire);
            record.setIsVip(true);
            record.setCreatedAt(now);
            record.setUpdatedAt(now);
            userMemberMapper.insert(record);
        } else {
            record.setPackageId(pkg.getId());
            record.setExpireTime(expire);
            record.setIsVip(true);
            record.setUpdatedAt(now);
            userMemberMapper.updateById(record);
        }
        return record;
    }

    private void refreshVipIfExpired(Long userId) {
        UserMemberEntity record = userMemberMapper.selectOne(
                new LambdaQueryWrapper<UserMemberEntity>().eq(UserMemberEntity::getUserId, userId)
        );
        if (record == null || !Boolean.TRUE.equals(record.getIsVip())) {
            return;
        }
        if (record.getExpireTime() != null && record.getExpireTime().isBefore(LocalDateTime.now())) {
            record.setIsVip(false);
            record.setUpdatedAt(LocalDateTime.now());
            userMemberMapper.updateById(record);
        }
    }

    private List<Object> parseRights(String raw) {
        if (raw == null || raw.isBlank()) {
            return Collections.emptyList();
        }
        try {
            return MAPPER.readValue(raw, new TypeReference<List<Object>>() {});
        } catch (Exception ex) {
            return Collections.emptyList();
        }
    }
}
