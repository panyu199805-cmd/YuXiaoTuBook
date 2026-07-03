package com.yuxiaotu.trade.controller;

import com.yuxiaotu.trade.common.ApiResponse;
import com.yuxiaotu.trade.dto.request.CreateOrderRequest;
import com.yuxiaotu.trade.dto.response.OrderVO;
import com.yuxiaotu.trade.security.JwtAuthFilter;
import com.yuxiaotu.trade.service.OrderService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {
    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping("")
    public ApiResponse<OrderVO> create(@Valid @RequestBody CreateOrderRequest body, HttpServletRequest request) {
        Long userId = currentUserId(request);
        OrderVO order = orderService.createOrder(userId, body);
        return ApiResponse.ok(order, "订单创建成功");
    }

    @GetMapping("")
    public ApiResponse<List<OrderVO>> list(HttpServletRequest request) {
        return ApiResponse.ok(orderService.listOrders(currentUserId(request)));
    }

    @GetMapping("/{orderId}")
    public ApiResponse<OrderVO> detail(@PathVariable Long orderId, HttpServletRequest request) {
        return ApiResponse.ok(orderService.getOrder(currentUserId(request), orderId));
    }

    @PostMapping("/{orderId}/mock-pay")
    public ApiResponse<OrderVO> mockPay(@PathVariable Long orderId, HttpServletRequest request) {
        OrderVO order = orderService.mockPay(currentUserId(request), orderId);
        return ApiResponse.ok(order, "支付成功");
    }

    @PostMapping("/{orderId}/cancel")
    public ApiResponse<OrderVO> cancel(@PathVariable Long orderId, HttpServletRequest request) {
        OrderVO order = orderService.cancel(currentUserId(request), orderId);
        return ApiResponse.ok(order, "订单已取消");
    }

    private Long currentUserId(HttpServletRequest request) {
        return (Long) request.getAttribute(JwtAuthFilter.USER_ID_ATTR);
    }
}
