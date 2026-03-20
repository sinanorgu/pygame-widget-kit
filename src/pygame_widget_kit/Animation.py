from __future__ import annotations

from typing import Any, Callable


class Easing:
    @staticmethod
    def linear(t: float) -> float:
        return t

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        return 1 - ((-2 * t + 2) ** 2) / 2

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        return 1 - (1 - t) ** 3


class Animation:
    def __init__(
        self,
        duration: float,
        easing: Callable[[float], float] | None = None,
        delay: float = 0.0,
        on_start: Callable[[], None] | None = None,
        on_update: Callable[[float], None] | None = None,
        on_complete: Callable[[], None] | None = None,
        key: Any = None,
    ):
        self.duration = max(0.000001, float(duration))
        self.easing = easing or Easing.linear
        self.delay = max(0.0, float(delay))

        self.on_start = on_start
        self.on_update = on_update
        self.on_complete = on_complete

        self.key = key

        self.elapsed = 0.0
        self.started = False
        self.finished = False
        self.paused = False

    def start(self):
        if self.started:
            return
        self.started = True
        if self.on_start is not None:
            self.on_start()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def cancel(self):
        self.finished = True

    def update(self, dt: float):
        if self.finished or self.paused:
            return

        self.elapsed += max(0.0, dt)

        if self.elapsed < self.delay:
            return

        if not self.started:
            self.start()

        local_elapsed = self.elapsed - self.delay
        raw_t = min(1.0, local_elapsed / self.duration)
        eased_t = max(0.0, min(1.0, self.easing(raw_t)))

        self._apply(eased_t)

        if self.on_update is not None:
            self.on_update(eased_t)

        if raw_t >= 1.0:
            self.finished = True
            if self.on_complete is not None:
                self.on_complete()

    def _apply(self, eased_t: float):
        raise NotImplementedError


class PropertyAnimation(Animation):
    def __init__(
        self,
        getter: Callable[[], Any],
        setter: Callable[[Any], None],
        to_value: Any,
        duration: float,
        from_value: Any = None,
        easing: Callable[[float], float] | None = None,
        delay: float = 0.0,
        on_start: Callable[[], None] | None = None,
        on_update: Callable[[float], None] | None = None,
        on_complete: Callable[[], None] | None = None,
        interpolator: Callable[[Any, Any, float], Any] | None = None,
        key: Any = None,
    ):
        super().__init__(
            duration=duration,
            easing=easing,
            delay=delay,
            on_start=on_start,
            on_update=on_update,
            on_complete=on_complete,
            key=key,
        )
        self.getter = getter
        self.setter = setter
        self.to_value = to_value
        self.from_value = from_value
        self.interpolator = interpolator or interpolate_value

    def start(self):
        if self.from_value is None:
            self.from_value = self.getter()
        super().start()

    def _apply(self, eased_t: float):
        value = self.interpolator(self.from_value, self.to_value, eased_t)
        self.setter(value)


class AnimationManager:
    def __init__(self):
        self.animations: list[Animation] = []

    def add(self, animation: Animation):
        if animation.key is not None:
            self.animations = [a for a in self.animations if a.key != animation.key]
        self.animations.append(animation)
        return animation

    def update(self, dt: float):
        if not self.animations:
            return

        for animation in list(self.animations):
            animation.update(dt)

        self.animations = [a for a in self.animations if not a.finished]

    def clear(self):
        self.animations.clear()

    def clear_key(self, key: Any):
        self.animations = [a for a in self.animations if a.key != key]

    def animate(
        self,
        getter: Callable[[], Any],
        setter: Callable[[Any], None],
        to_value: Any,
        duration: float,
        from_value: Any = None,
        easing: Callable[[float], float] | None = None,
        delay: float = 0.0,
        on_start: Callable[[], None] | None = None,
        on_update: Callable[[float], None] | None = None,
        on_complete: Callable[[], None] | None = None,
        interpolator: Callable[[Any, Any, float], Any] | None = None,
        key: Any = None,
    ):
        animation = PropertyAnimation(
            getter=getter,
            setter=setter,
            to_value=to_value,
            duration=duration,
            from_value=from_value,
            easing=easing,
            delay=delay,
            on_start=on_start,
            on_update=on_update,
            on_complete=on_complete,
            interpolator=interpolator,
            key=key,
        )
        return self.add(animation)

    def animate_attr(
        self,
        target: Any,
        attr_name: str,
        to_value: Any,
        duration: float,
        from_value: Any = None,
        easing: Callable[[float], float] | None = None,
        delay: float = 0.0,
        on_start: Callable[[], None] | None = None,
        on_update: Callable[[float], None] | None = None,
        on_complete: Callable[[], None] | None = None,
        interpolator: Callable[[Any, Any, float], Any] | None = None,
        key: Any = None,
    ):
        animation_key = key if key is not None else (id(target), attr_name)

        def getter():
            return getattr(target, attr_name)

        def setter(value):
            setattr(target, attr_name, value)

        return self.animate(
            getter=getter,
            setter=setter,
            to_value=to_value,
            duration=duration,
            from_value=from_value,
            easing=easing,
            delay=delay,
            on_start=on_start,
            on_update=on_update,
            on_complete=on_complete,
            interpolator=interpolator,
            key=animation_key,
        )


def interpolate_value(a: Any, b: Any, t: float):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a + (b - a) * t

    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)) and len(a) == len(b):
        values = [interpolate_value(x, y, t) for x, y in zip(a, b)]
        if isinstance(a, tuple):
            return tuple(values)
        return values

    try:
        return a.lerp(b, t)
    except Exception:
        pass

    return b if t >= 1.0 else a
