package com.yuxiaotu.trade.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.yuxiaotu.trade.common.BizException;
import com.yuxiaotu.trade.common.ErrorCodes;
import com.yuxiaotu.trade.config.TradeProperties;
import com.yuxiaotu.trade.dto.request.CreateOrderRequest;
import com.yuxiaotu.trade.dto.response.OrderVO;
import com.yuxiaotu.trade.entity.BookEntity;
import com.yuxiaotu.trade.entity.OrderEntity;
import com.yuxiaotu.trade.entity.OrderItemEntity;
import com.yuxiaotu.trade.mapper.BookMapper;
import com.yuxiaotu.trade.mapper.OrderItemMapper;
import com.yuxiaotu.trade.mapper.OrderMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
public class OrderService {
    private static final Pattern PHONE = Pattern.compile("^1\\d{10}$");
    private static final DateTimeFormatter ORDER_NO_TIME = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");

    private final OrderMapper orderMapper;
    private final OrderItemMapper orderItemMapper;
    private final BookMapper bookMapper;
    private final OrderViewHelper orderViewHelper;
    private final TradeProperties properties;

    public OrderService(OrderMapper orderMapper, OrderItemMapper orderItemMapper, BookMapper bookMapper,
                        OrderViewHelper orderViewHelper, TradeProperties properties) {
        this.orderMapper = orderMapper;
        this.orderItemMapper = orderItemMapper;
        this.bookMapper = bookMapper;
        this.orderViewHelper = orderViewHelper;
        this.properties = properties;
    }

    @Transactional
    public OrderVO createOrder(Long userId, CreateOrderRequest req) {
        if (req.getQuantity() == null || req.getQuantity() < 1) {
            throw new BizException(400, "数量无效");
        }
        if (!PHONE.matcher(req.getReceiverPhone()).matches()) {
            throw new BizException(400, "手机号格式错误");
        }
        BookEntity book = bookMapper.selectById(req.getBookId());
        if (book == null || !"published".equals(book.getStatus())) {
            throw new BizException(ErrorCodes.OFF_SHELF, "书籍已下架");
        }
        if (book.getStock() < req.getQuantity()) {
            throw new BizException(ErrorCodes.STOCK, "库存不足");
        }

        OrderEntity order = new OrderEntity();
        order.setOrderNo("YT" + LocalDateTime.now().format(ORDER_NO_TIME));
        order.setUserId(userId);
        order.setTotalAmount(book.getPrice().multiply(BigDecimal.valueOf(req.getQuantity())));
        order.setStatus("pending_payment");
        order.setReceiverName(req.getReceiverName());
        order.setReceiverPhone(req.getReceiverPhone());
        order.setReceiverAddress(req.getReceiverAddress());
        order.setCreatedAt(LocalDateTime.now());
        order.setUpdatedAt(LocalDateTime.now());
        orderMapper.insert(order);

        OrderItemEntity item = new OrderItemEntity();
        item.setOrderId(order.getId());
        item.setBookId(book.getId());
        item.setBookTitle(book.getTitle());
        item.setPrice(book.getPrice());
        item.setQuantity(req.getQuantity());
        orderItemMapper.insert(item);

        return orderViewHelper.toVo(order);
    }

    public List<OrderVO> listOrders(Long userId) {
        List<OrderEntity> orders = orderMapper.selectList(
                new LambdaQueryWrapper<OrderEntity>()
                        .eq(OrderEntity::getUserId, userId)
                        .orderByDesc(OrderEntity::getCreatedAt)
        );
        return orders.stream().map(orderViewHelper::toVo).collect(Collectors.toList());
    }

    public OrderVO getOrder(Long userId, Long orderId) {
        OrderEntity order = orderMapper.selectOne(
                new LambdaQueryWrapper<OrderEntity>()
                        .eq(OrderEntity::getId, orderId)
                        .eq(OrderEntity::getUserId, userId)
        );
        if (order == null) {
            throw new BizException(404, "订单不存在");
        }
        return orderViewHelper.toVo(order);
    }

    @Transactional
    public OrderVO mockPay(Long userId, Long orderId) {
        if (!properties.isMockPayEnabled()) {
            throw new BizException(ErrorCodes.MOCK_PAY_DISABLED, "模拟支付未开启");
        }
        OrderEntity order = orderMapper.selectOne(
                new LambdaQueryWrapper<OrderEntity>()
                        .eq(OrderEntity::getId, orderId)
                        .eq(OrderEntity::getUserId, userId)
        );
        if (order == null) {
            throw new BizException(404, "订单不存在");
        }
        if (!"pending_payment".equals(order.getStatus())) {
            throw new BizException(ErrorCodes.ORDER_STATUS, "订单状态不允许支付");
        }
        OrderItemEntity item = orderItemMapper.selectOne(
                new LambdaQueryWrapper<OrderItemEntity>().eq(OrderItemEntity::getOrderId, order.getId())
        );
        if (item == null) {
            throw new BizException(400, "订单明细不存在");
        }
        BookEntity book = bookMapper.selectByIdForUpdate(item.getBookId());
        if (book == null || book.getStock() < item.getQuantity()) {
            throw new BizException(ErrorCodes.STOCK, "库存不足");
        }
        book.setStock(book.getStock() - item.getQuantity());
        bookMapper.updateById(book);

        order.setStatus("paid");
        order.setPayTime(LocalDateTime.now());
        order.setUpdatedAt(LocalDateTime.now());
        orderMapper.updateById(order);
        return orderViewHelper.toVo(order);
    }

    @Transactional
    public OrderVO cancel(Long userId, Long orderId) {
        OrderEntity order = orderMapper.selectOne(
                new LambdaQueryWrapper<OrderEntity>()
                        .eq(OrderEntity::getId, orderId)
                        .eq(OrderEntity::getUserId, userId)
        );
        if (order == null) {
            throw new BizException(404, "订单不存在");
        }
        if ("cancelled".equals(order.getStatus()) || "completed".equals(order.getStatus())) {
            throw new BizException(400, "订单状态不可取消");
        }
        if ("paid".equals(order.getStatus())) {
            OrderItemEntity item = orderItemMapper.selectOne(
                    new LambdaQueryWrapper<OrderItemEntity>().eq(OrderItemEntity::getOrderId, order.getId())
            );
            if (item != null) {
                BookEntity book = bookMapper.selectByIdForUpdate(item.getBookId());
                if (book != null) {
                    book.setStock(book.getStock() + item.getQuantity());
                    bookMapper.updateById(book);
                }
            }
        }
        order.setStatus("cancelled");
        order.setUpdatedAt(LocalDateTime.now());
        orderMapper.updateById(order);
        return orderViewHelper.toVo(order);
    }

    @Transactional
    public void cancelTimedOutOrders() {
        LocalDateTime deadline = LocalDateTime.now().minusMinutes(properties.getOrderTimeoutMinutes());
        List<OrderEntity> stale = orderMapper.selectList(
                new LambdaQueryWrapper<OrderEntity>()
                        .eq(OrderEntity::getStatus, "pending_payment")
                        .lt(OrderEntity::getCreatedAt, deadline)
        );
        for (OrderEntity order : stale) {
            order.setStatus("cancelled");
            order.setUpdatedAt(LocalDateTime.now());
            orderMapper.updateById(order);
        }
    }
}
