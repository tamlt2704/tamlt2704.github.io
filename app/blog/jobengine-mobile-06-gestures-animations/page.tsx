import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Gestures & Animations: Swipe, Drag, Delight"
            date="May 7, 2026"
            series="Job Engine Mobile"
            chapter={6}
            prevSlug="jobengine-mobile-05-performance"
            prevTitle="Performance"
            nextSlug="jobengine-mobile-07-offline-persistence"
            nextTitle="Offline & Persistence"
        >
            <Section title="The Problem">
                <Paragraph>
                    Karen wants to cancel a job by swiping left — like deleting an email. Captain Deadline wants draggable DAG nodes. The web dashboard has onClick. Mobile has an entire vocabulary of touch: tap, long press, swipe, pinch, pan, fling.
                </Paragraph>
            </Section>

            <Section title="Why Reanimated?">
                <Paragraph>
                    The built-in Animated API runs on the JS thread. When JS is busy (processing SSE events), animations stutter. Reanimated runs on the UI thread — completely independent of JavaScript. Even if your JS thread freezes, the animation stays at 60fps.
                </Paragraph>
                <Code lang="bash">{`npx expo install react-native-gesture-handler react-native-reanimated`}</Code>
            </Section>

            <Section title="Swipe-to-Cancel">
                <Code lang="tsx" title="src/components/SwipeableJobCard.tsx">{`import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, { useSharedValue, useAnimatedStyle, withSpring, runOnJS } from "react-native-reanimated";

const SWIPE_THRESHOLD = -120;

export function SwipeableJobCard({ job, onPress }: Props) {
  const translateX = useSharedValue(0);

  const panGesture = Gesture.Pan()
    .activeOffsetX([-10, 10])
    .onUpdate((e) => {
      if (e.translationX < 0 && (job.status === "PENDING" || job.status === "RUNNING")) {
        translateX.value = e.translationX;
      }
    })
    .onEnd((e) => {
      if (e.translationX < SWIPE_THRESHOLD) {
        runOnJS(confirmCancel)();
      } else {
        translateX.value = withSpring(0);
      }
    });

  const cardStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={cardStyle}>
        <JobCard job={job} onPress={onPress} />
      </Animated.View>
    </GestureDetector>
  );
}`}</Code>
            </Section>

            <Section title="Long Press + Haptics">
                <Paragraph>
                    Long press a card for a context menu with haptic feedback:
                </Paragraph>
                <Code lang="tsx">{`import * as Haptics from "expo-haptics";

const longPressGesture = Gesture.LongPress()
  .minDuration(500)
  .onStart(() => {
    scale.value = withSpring(0.95);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  })
  .onEnd(() => {
    scale.value = withSpring(1);
    setShowActions(true);
  });`}</Code>
            </Section>

            <Section title="Animated Status Transitions">
                <Paragraph>
                    When a job status changes via SSE, pulse the badge:
                </Paragraph>
                <Code lang="tsx">{`useEffect(() => {
  scale.value = withSequence(
    withSpring(1.2, { damping: 8 }),
    withSpring(1, { damping: 12 })
  );
}, [status]);`}</Code>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Swipe a PENDING job left → red &quot;Cancel&quot; background reveals → release past threshold → confirmation dialog. Long press a card → haptic feedback + scale animation → action sheet. All animations run on the UI thread — block JS and they still work.
                </Paragraph>
                <Paragraph>
                    Karen swipes a job left. The red background slides in. She releases. &quot;Cancel Job?&quot; She taps yes. The card slides off screen. Satisfying. &quot;What happens when I&apos;m on the subway with no signal?&quot;
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
