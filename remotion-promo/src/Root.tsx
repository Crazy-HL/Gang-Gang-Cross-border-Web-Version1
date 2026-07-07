import {Composition} from 'remotion';
import {GangGangPromo} from './GangGangPromo';

export const RemotionRoot = () => {
  return (
    <Composition
      id="GangGangPromo"
      component={GangGangPromo}
      durationInFrames={840}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
