package com.yuxiaotu.trade.task;

import com.yuxiaotu.trade.service.OrderService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class OrderTimeoutJob {
    private static final Logger log = LoggerFactory.getLogger(OrderTimeoutJob.class);
    private final OrderService orderService;

    public OrderTimeoutJob(OrderService orderService) {
        this.orderService = orderService;
    }

    @Scheduled(fixedDelay = 60_000)
    public void cancelExpiredOrders() {
        orderService.cancelTimedOutOrders();
        log.debug("Order timeout job executed");
    }
}
