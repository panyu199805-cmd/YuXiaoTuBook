package com.yuxiaotu.trade.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.yuxiaotu.trade.entity.BookEntity;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

public interface BookMapper extends BaseMapper<BookEntity> {

    @Select("SELECT * FROM book WHERE id = #{id} FOR UPDATE")
    BookEntity selectByIdForUpdate(@Param("id") Long id);
}
