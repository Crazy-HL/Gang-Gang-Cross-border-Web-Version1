import React from 'react';
import {Audio} from '@remotion/media';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const blue = '#2563eb';
const ink = '#07111f';
const gold = '#f6b84b';
const orange = '#fb923c';
const slate = '#0f172a';

const clamp = {
  extrapolateLeft: 'clamp' as const,
  extrapolateRight: 'clamp' as const,
};

const ease = Easing.bezier(0.16, 1, 0.3, 1);

const sec = (seconds: number, fps: number) => Math.round(seconds * fps);

const Scene: React.FC<{
  from: number;
  duration: number;
  children: React.ReactNode;
}> = ({from, duration, children}) => {
  return (
    <Sequence from={from} durationInFrames={duration}>
      <AbsoluteFill>{children}</AbsoluteFill>
    </Sequence>
  );
};

const Background: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        'radial-gradient(circle at 78% 7%, rgba(251,146,60,.34), transparent 24%), radial-gradient(circle at 8% 88%, rgba(37,99,235,.24), transparent 30%), linear-gradient(145deg,#ffffff 0%,#eef7ff 47%,#fff7ed 100%)',
    }}
  />
);

const Brand: React.FC<{light?: boolean}> = ({light}) => (
  <div
    style={{
      position: 'absolute',
      top: 70,
      left: 70,
      display: 'flex',
      alignItems: 'center',
      gap: 18,
      color: light ? '#fff' : slate,
      zIndex: 20,
    }}
  >
    <Img
      src={staticFile('brand-icon.png')}
      style={{
        width: 62,
        height: 62,
        borderRadius: 16,
        background: 'rgba(255,255,255,.84)',
        boxShadow: '0 18px 40px rgba(15,23,42,.12)',
      }}
    />
    <div>
      <div style={{fontSize: 30, fontWeight: 950, lineHeight: 1}}>港港跨境</div>
      <div
        style={{
          marginTop: 7,
          fontSize: 18,
          color: light ? 'rgba(255,255,255,.72)' : '#64748b',
          fontWeight: 700,
        }}
      >
        上架风险预检
      </div>
    </div>
  </div>
);

const Caption: React.FC<{
  kicker?: string;
  title: string;
  body?: string;
  align?: 'top' | 'bottom' | 'center';
  light?: boolean;
}> = ({kicker, title, body, align = 'bottom', light}) => {
  const top = align === 'top' ? 190 : align === 'center' ? 610 : undefined;
  const bottom = align === 'bottom' ? 130 : undefined;
  return (
    <div
      style={{
        position: 'absolute',
        left: 70,
        right: 70,
        top,
        bottom,
        zIndex: 30,
        color: light ? '#fff' : slate,
      }}
    >
      {kicker ? (
        <div
          style={{
            display: 'inline-flex',
            borderRadius: 999,
            padding: '15px 22px',
            background: light ? 'rgba(255,255,255,.14)' : 'rgba(255,255,255,.84)',
            border: `2px solid ${light ? 'rgba(255,255,255,.18)' : 'rgba(37,99,235,.16)'}`,
            color: light ? '#bfdbfe' : blue,
            fontSize: 24,
            fontWeight: 900,
            boxShadow: light ? 'none' : '0 18px 45px rgba(37,99,235,.12)',
          }}
        >
          {kicker}
        </div>
      ) : null}
      <div
        style={{
          marginTop: kicker ? 30 : 0,
          fontSize: 76,
          lineHeight: 1.08,
          letterSpacing: 0,
          fontWeight: 950,
          textShadow: light ? '0 22px 70px rgba(0,0,0,.28)' : 'none',
          whiteSpace: 'pre-line',
        }}
      >
        {title}
      </div>
      {body ? (
        <div
          style={{
            marginTop: 30,
            maxWidth: 850,
            fontSize: 31,
            lineHeight: 1.52,
            color: light ? 'rgba(255,255,255,.78)' : '#475569',
            fontWeight: 650,
            whiteSpace: 'pre-line',
          }}
        >
          {body}
        </div>
      ) : null}
    </div>
  );
};

const StoryToast: React.FC<{
  frame: number;
  start: number;
  top: number;
  left?: number;
  right?: number;
  label: string;
  title: string;
  body: string;
  tone?: 'worry' | 'safe' | 'neutral';
}> = ({frame, start, top, left = 70, right = 70, label, title, body, tone = 'neutral'}) => {
  const opacity = interpolate(frame, [start, start + 18], [0, 1], clamp);
  const y = interpolate(frame, [start, start + 22], [44, 0], {...clamp, easing: ease});
  const accent = tone === 'worry' ? '#ef4444' : tone === 'safe' ? '#16a34a' : blue;
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left,
        right,
        zIndex: 32,
        borderRadius: 38,
        padding: '30px 34px',
        background: 'rgba(255,255,255,.92)',
        border: `2px solid ${tone === 'worry' ? 'rgba(239,68,68,.16)' : 'rgba(37,99,235,.14)'}`,
        boxShadow: '0 34px 90px rgba(15,23,42,.16)',
        opacity,
        transform: `translateY(${y}px)`,
      }}
    >
      <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
        <div
          style={{
            width: 18,
            height: 18,
            borderRadius: 999,
            background: accent,
            boxShadow: `0 0 0 9px ${tone === 'worry' ? 'rgba(239,68,68,.12)' : 'rgba(37,99,235,.12)'}`,
          }}
        />
        <div style={{fontSize: 22, color: accent, fontWeight: 950}}>{label}</div>
      </div>
      <div style={{marginTop: 18, fontSize: 42, lineHeight: 1.12, color: slate, fontWeight: 950, whiteSpace: 'pre-line'}}>
        {title}
      </div>
      <div style={{marginTop: 16, fontSize: 26, lineHeight: 1.44, color: '#475569', fontWeight: 700, whiteSpace: 'pre-line'}}>
        {body}
      </div>
    </div>
  );
};

const MessageStack: React.FC<{frame: number; start: number}> = ({frame, start}) => {
  const messages = [
    {name: '运营', text: '新品明天上架，图片和标题能直接用吗？', color: '#fee2e2'},
    {name: '老板', text: '先别急，侵权退货一次就麻烦了。', color: '#ffedd5'},
    {name: '你', text: '我先用港港跨境跑一遍预检。', color: '#dbeafe'},
  ];
  return (
    <div style={{position: 'absolute', left: 70, right: 70, top: 260, zIndex: 31}}>
      {messages.map((message, index) => {
        const localStart = start + index * 16;
        const opacity = interpolate(frame, [localStart, localStart + 16], [0, 1], clamp);
        const y = interpolate(frame, [localStart, localStart + 18], [34, 0], {...clamp, easing: ease});
        return (
          <div
            key={message.name}
            style={{
              marginTop: index === 0 ? 0 : 18,
              width: index === 1 ? 790 : 850,
              marginLeft: index === 1 ? 116 : 0,
              borderRadius: 32,
              padding: '24px 28px',
              background: message.color,
              color: slate,
              boxShadow: '0 28px 70px rgba(15,23,42,.12)',
              opacity,
              transform: `translateY(${y}px)`,
            }}
          >
            <div style={{fontSize: 21, fontWeight: 950, color: index === 2 ? blue : '#64748b'}}>{message.name}</div>
            <div style={{marginTop: 8, fontSize: 31, lineHeight: 1.28, fontWeight: 900}}>{message.text}</div>
          </div>
        );
      })}
    </div>
  );
};

const HomepagePhone: React.FC<{
  frame: number;
  start: number;
  end: number;
  scaleFrom?: number;
  scaleTo?: number;
  yFrom?: number;
  yTo?: number;
  scrollFrom?: number;
  scrollTo?: number;
}> = ({
  frame,
  start,
  end,
  scaleFrom = 1.04,
  scaleTo = 1.14,
  yFrom = 0,
  yTo = -70,
  scrollFrom = 0,
  scrollTo = 0,
}) => {
  const scale = interpolate(frame, [start, end], [scaleFrom, scaleTo], {
    ...clamp,
    easing: ease,
  });
  const y = interpolate(frame, [start, end], [yFrom, yTo], {...clamp, easing: ease});
  const scrollY = interpolate(frame, [start, end], [scrollFrom, scrollTo], {
    ...clamp,
    easing: ease,
  });
  return (
    <div
      style={{
        position: 'absolute',
        left: 93,
        top: 250 + y,
        width: 894,
        height: 1230,
        borderRadius: 62,
        overflow: 'hidden',
        background: '#fff',
        boxShadow: '0 46px 115px rgba(15,23,42,.22)',
        border: '10px solid rgba(255,255,255,.84)',
        transform: `scale(${scale})`,
        transformOrigin: 'center center',
      }}
    >
      <Img
        src={staticFile('homepage-full.png')}
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: '100%',
          height: 'auto',
          transform: `translateY(${-scrollY}px)`,
        }}
      />
    </div>
  );
};

const CheckLine: React.FC<{text: string; delay: number; frame: number}> = ({text, delay, frame}) => {
  const opacity = interpolate(frame, [delay, delay + 18], [0, 1], clamp);
  const x = interpolate(frame, [delay, delay + 18], [36, 0], {...clamp, easing: ease});
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 18,
        opacity,
        transform: `translateX(${x}px)`,
        marginTop: 20,
      }}
    >
      <div
        style={{
          width: 46,
          height: 46,
          borderRadius: 999,
          background: blue,
          color: '#fff',
          display: 'grid',
          placeItems: 'center',
          fontSize: 27,
          fontWeight: 950,
        }}
      >
        ✓
      </div>
      <div style={{fontSize: 36, fontWeight: 900, color: slate}}>{text}</div>
    </div>
  );
};

const ReportCard: React.FC<{frame: number; start: number}> = ({frame, start}) => {
  const opacity = interpolate(frame, [start, start + 20], [0, 1], clamp);
  const y = interpolate(frame, [start, start + 24], [80, 0], {...clamp, easing: ease});
  const bar = interpolate(frame, [start + 22, start + 82], [0, 82], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: 78,
        right: 78,
        top: 525,
        borderRadius: 46,
        background: 'rgba(255,255,255,.92)',
        border: '2px solid rgba(37,99,235,.12)',
        boxShadow: '0 36px 90px rgba(15,23,42,.16)',
        padding: 46,
        opacity,
        transform: `translateY(${y}px)`,
      }}
    >
      <div style={{display: 'flex', justifyContent: 'space-between', gap: 28}}>
        <div>
          <div style={{fontSize: 25, color: blue, fontWeight: 950}}>检测报告</div>
          <div style={{marginTop: 14, fontSize: 44, lineHeight: 1.18, fontWeight: 950, color: slate}}>
            新品运动鞋上架资料
          </div>
        </div>
        <div
          style={{
            height: 86,
            minWidth: 136,
            borderRadius: 999,
            background: '#ffedd5',
            color: '#9a3412',
            display: 'grid',
            placeItems: 'center',
            fontSize: 26,
            fontWeight: 950,
          }}
        >
          中风险
        </div>
      </div>
      <div style={{marginTop: 38}}>
        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 24, color: '#64748b', fontWeight: 800}}>
          <span>综合风险分</span>
          <span>{Math.round(bar)} / 100</span>
        </div>
        <div style={{height: 24, borderRadius: 999, background: '#e2e8f0', marginTop: 14, overflow: 'hidden'}}>
          <div
            style={{
              width: `${bar}%`,
              height: '100%',
              borderRadius: 999,
              background: `linear-gradient(90deg, ${blue}, #38bdf8, ${orange})`,
            }}
          />
        </div>
      </div>
      <div style={{marginTop: 34}}>
        <CheckLine text="标题关键词：建议替换" delay={start + 34} frame={frame} />
        <CheckLine text="鞋面外观：发现相似点" delay={start + 52} frame={frame} />
        <CheckLine text="主图素材：给出处理建议" delay={start + 70} frame={frame} />
      </div>
      <div
        style={{
          marginTop: 36,
          borderRadius: 28,
          padding: '24px 28px',
          background: '#eff6ff',
          color: blue,
          fontSize: 28,
          lineHeight: 1.38,
          fontWeight: 900,
        }}
      >
        不是让你别卖，而是先把容易踩坑的地方改掉。
      </div>
    </div>
  );
};

const CtaButton: React.FC<{frame: number; start: number}> = ({frame, start}) => {
  const opacity = interpolate(frame, [start, start + 18], [0, 1], clamp);
  const scale = interpolate(frame, [start, start + 24, start + 48], [0.86, 1.03, 1], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: 130,
        right: 130,
        bottom: 170,
        height: 100,
        borderRadius: 999,
        background: `linear-gradient(135deg, ${blue}, #4f7df3)`,
        color: '#fff',
        display: 'grid',
        placeItems: 'center',
        fontSize: 36,
        fontWeight: 950,
        boxShadow: '0 28px 72px rgba(37,99,235,.34)',
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      免费检测
    </div>
  );
};

const AudioTracks: React.FC<{fps: number}> = ({fps}) => {
  const voiceStart = sec(0.65, fps);
  return (
    <>
      <Audio
        src={staticFile('audio/story-bgm.wav')}
        volume={(f) =>
          interpolate(f, [0, sec(1.2, fps), sec(25.8, fps), sec(28, fps)], [0, 0.16, 0.16, 0], clamp)
        }
      />
      <Sequence from={voiceStart} durationInFrames={sec(23.8, fps)} layout="none">
        <Audio
          src={staticFile('audio/voiceover-real.mp3')}
          volume={(f) => interpolate(f, [0, sec(0.35, fps), sec(22.4, fps), sec(23.3, fps)], [0, 1, 1, 0], clamp)}
        />
      </Sequence>
    </>
  );
};

export const GangGangPromo: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const intro = sec(0, fps);
  const introDur = sec(5.2, fps);
  const input = sec(5.2, fps);
  const inputDur = sec(6.4, fps);
  const scan = sec(11.6, fps);
  const scanDur = sec(6.1, fps);
  const report = sec(17.7, fps);
  const reportDur = sec(5.4, fps);
  const end = sec(23.1, fps);
  const endDur = sec(4.9, fps);

  return (
    <AbsoluteFill style={{fontFamily: 'Arial, PingFang SC, Helvetica Neue, sans-serif', background: '#fff'}}>
      <AudioTracks fps={fps} />
      <Scene from={intro} duration={introDur}>
        <Background />
        <Brand />
        <HomepagePhone frame={frame} start={intro} end={intro + introDur} scaleFrom={0.98} scaleTo={1.08} yFrom={165} yTo={80} />
        <MessageStack frame={frame} start={intro + 16} />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(180deg, rgba(255,255,255,0) 28%, rgba(255,255,255,.92) 68%, #fff 100%)',
          }}
        />
        <Caption
          kicker="新品要上架"
          title={'先别急着卖\n先查一遍风险'}
          body={'跨境卖家最怕的不是慢一步，而是上架后才发现商标、外观、素材有问题。'}
        />
      </Scene>

      <Scene from={input} duration={inputDur}>
        <Background />
        <Brand />
        <HomepagePhone
          frame={frame}
          start={input}
          end={input + inputDur}
          scaleFrom={1.22}
          scaleTo={1.32}
          yFrom={-245}
          yTo={-405}
          scrollFrom={650}
          scrollTo={1260}
        />
        <StoryToast
          frame={frame}
          start={input + 18}
          top={205}
          label="转折"
          title={'打开港港跨境\n把资料先丢进来'}
          body={'图片、标题、详情文案和目标平台，先做一次上架前预检。'}
        />
        <div
          style={{
            position: 'absolute',
            left: 70,
            right: 70,
            bottom: 156,
            borderRadius: 42,
            background: 'rgba(255,255,255,.92)',
            border: '2px solid rgba(37,99,235,.12)',
            padding: 40,
            boxShadow: '0 38px 92px rgba(15,23,42,.16)',
          }}
        >
          <div style={{fontSize: 26, color: blue, fontWeight: 950}}>卖家的动作</div>
          <div style={{marginTop: 12, fontSize: 62, lineHeight: 1.08, fontWeight: 950, color: slate}}>先提交资料</div>
          <div style={{marginTop: 24}}>
            <CheckLine text="商品图片" delay={input + 24} frame={frame} />
            <CheckLine text="标题 / 详情文案" delay={input + 42} frame={frame} />
            <CheckLine text="目标市场和平台" delay={input + 60} frame={frame} />
          </div>
        </div>
      </Scene>

      <Scene from={scan} duration={scanDur}>
        <AbsoluteFill style={{background: ink}} />
        <Brand light />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle at 50% 34%, rgba(37,99,235,.52), transparent 27%), radial-gradient(circle at 78% 78%, rgba(251,146,60,.38), transparent 30%)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            left: 90,
            right: 90,
            top: 380,
            height: 740,
            borderRadius: 58,
            background: 'rgba(255,255,255,.08)',
            border: '2px solid rgba(255,255,255,.14)',
            boxShadow: 'inset 0 0 120px rgba(37,99,235,.14)',
          }}
        >
          {['商标近似', '外观相似', '版权素材'].map((item, index) => {
            const localStart = scan + 22 + index * 38;
            const opacity = interpolate(frame, [localStart, localStart + 18], [0, 1], clamp);
            const y = interpolate(frame, [localStart, localStart + 18], [40, 0], {...clamp, easing: ease});
            const status = ['建议复核', '发现相似点', '建议替换'][index];
            return (
              <div
                key={item}
                style={{
                  position: 'absolute',
                  left: 52,
                  right: 52,
                  top: 82 + index * 176,
                  height: 124,
                  borderRadius: 34,
                  background: 'rgba(255,255,255,.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0 34px',
                  color: '#fff',
                  opacity,
                  transform: `translateY(${y}px)`,
                }}
              >
                <div style={{fontSize: 40, fontWeight: 950}}>{item}</div>
                <div style={{fontSize: 26, color: index === 0 ? gold : '#93c5fd', fontWeight: 950}}>
                  {status}
                </div>
              </div>
            );
          })}
        </div>
        <Caption
          align="bottom"
          light
          title={'系统先替你\n把坑扫出来'}
          body={'商标近似、外观相似、图片素材风险，提前看到，才有时间调整。'}
        />
      </Scene>

      <Scene from={report} duration={reportDur}>
        <Background />
        <Brand />
        <Caption align="top" kicker="检测完成" title={'风险不是终点\n建议才是重点'} body="风险等级、命中证据、处理建议，一页看清，卖家知道下一步怎么改。" />
        <ReportCard frame={frame} start={report + 35} />
      </Scene>

      <Scene from={end} duration={endDur}>
        <AbsoluteFill style={{background: `linear-gradient(145deg, ${ink}, #0b1f3a 52%, #132b4a)`}} />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle at 20% 20%, rgba(37,99,235,.45), transparent 27%), radial-gradient(circle at 86% 78%, rgba(251,184,75,.36), transparent 28%)',
          }}
        />
        <Brand light />
        <HomepagePhone frame={frame} start={end} end={end + endDur} scaleFrom={0.76} scaleTo={0.82} yFrom={650} yTo={590} />
        <Caption
          align="top"
          light
          kicker="港港跨境"
          title={'改完再上架\n少走一趟弯路'}
          body={'把商品资料发来，先查风险，再决定怎么卖。'}
        />
        <CtaButton frame={frame} start={end + 86} />
      </Scene>
    </AbsoluteFill>
  );
};
