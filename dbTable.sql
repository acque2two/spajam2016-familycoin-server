--家　        family  f_id, f_name
--人　        user    u_id, u_name, f_id, score, admin, adult, sex
--仕事　      work    f_id, w_id, w_name, g_id, point, u_id, w_text, image
--ジャンル    genre   g_id, g_name
--達成        unapproved    f_id, u_id, w_id, date
--未承認      achievement   f_id, u_id, w_id, date
--商品        product   p_id, f_id, p_name, p_point


-- DBがSQLiteからPostgreSQLに変更になっているので少し表現が異なる部分があります。
-- ex) 自動で増える数値: serial primary key
-- ex) 3億くらいを超える数値: bigint
-- ex) questionテーブルのq_idを使う外部参照: q_id bigint not null references question (q_id),

-- 家族ごと
create table family(
        f_id text primary key ,
        f_name text not null
);

-- ユーザ
create table users(
        u_id text primary key ,
        u_name text not null,
        f_id text not null references family (f_id),
        score int default '0',
        admin boolean not null,
        adult boolean not null,
        sex boolean not null
);

-- ジャンル
create table genre(
        g_id int primary key,
        g_name text not null
);

-- 仕事一覧
create table work(
        w_id serial primary key,
        w_text text not null,
        u_id text not null references users(u_id),
        f_id text not null references family(f_id),
        w_name text not null,
        g_id int not null references genre(g_id),
        point int not null,
        image text not null
);

-- アチーブ
create table achievement(
        f_id text not null references family(f_id),
        u_id text not null references users(u_id),
        w_id serial not null references work(w_id),
        date int not null
);

-- 未承認
create table unapproved(
        f_id text not null references family(f_id),
        u_id text not null references users(u_id),
        w_id serial not null references work(w_id),
        date int not null
);

-- 報酬
create table product(
        p_id serial primary key,
        p_name text not null,
        f_id text not null references family(f_id),
        p_point int not null
        );

-- ジャンル初期化
insert into genre values(
    1,
    '掃除'
);

insert into genre values(
    2,
    '料理'
);
insert into genre values(
    3,
    '洗濯'
);
insert into genre values(
    4,
    '勉強'
);
insert into genre values(
    5,
    '買い物'
);
insert into genre values(
    6,
    'その他'
);
