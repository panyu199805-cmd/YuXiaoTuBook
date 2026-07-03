package com.yuxiaotu.trade.controller;

import com.yuxiaotu.trade.common.ApiResponse;
import com.yuxiaotu.trade.dto.request.SubscribeRequest;
import com.yuxiaotu.trade.security.JwtAuthFilter;
import com.yuxiaotu.trade.service.MemberService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/member")
public class MemberController {
    private final MemberService memberService;

    public MemberController(MemberService memberService) {
        this.memberService = memberService;
    }

    @GetMapping("/packages")
    public ApiResponse<List<Map<String, Object>>> packages() {
        return ApiResponse.ok(memberService.listPackages());
    }

    @GetMapping("/status")
    public ApiResponse<Map<String, Object>> status(HttpServletRequest request) {
        return ApiResponse.ok(memberService.getStatus(currentUserId(request)));
    }

    @PostMapping("/subscribe")
    public ApiResponse<Map<String, Object>> subscribe(@Valid @RequestBody SubscribeRequest body,
                                                      HttpServletRequest request) {
        return ApiResponse.ok(memberService.subscribe(currentUserId(request), body));
    }

    @PostMapping("/orders/{orderId}/mock-pay")
    public ApiResponse<Map<String, Object>> mockPay(@PathVariable Long orderId, HttpServletRequest request) {
        Map<String, Object> data = memberService.mockPay(currentUserId(request), orderId);
        return ApiResponse.ok(data, "开通成功");
    }

    @PostMapping("/orders/{orderId}/pay")
    public ApiResponse<Void> realPay(@PathVariable Long orderId, HttpServletRequest request) {
        memberService.assertRealPaymentAvailable();
        return ApiResponse.fail(501, "真实支付尚未配置");
    }

    private Long currentUserId(HttpServletRequest request) {
        return (Long) request.getAttribute(JwtAuthFilter.USER_ID_ATTR);
    }
}
