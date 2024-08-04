import React, { useMemo } from "react";
import { motion, useMotionTemplate } from "framer-motion";

const DotBackground = React.memo(({ isMouseOver, mouseX, mouseY }) => {
  const maskImage = useMotionTemplate`
            radial-gradient(
              250px circle at ${mouseX}px ${mouseY}px,
              black 0%,
              transparent 100%
            )
          `;

  return (
    <div className="absolute inset-0">
      {/* Dot background div with enhanced mask */}
      <div className="w-full h-full bg-dot-white/[0.4]"></div>
      <motion.div
        className="absolute inset-0 bg-dot-thick-amber-500 transition-opacity duration-1000 ease-in-out"
        animate={{ opacity: isMouseOver ? 1 : 0 }}
        initial={{ opacity: 0 }}
        style={{
          WebkitMaskImage: maskImage,
          maskImage: maskImage,
        }}
      />
      <div className="absolute inset-0 bg-gray-900 [mask-image:radial-gradient(ellipse_at_20%_50%,transparent_0%,rgba(0,0,0,0.5)_30%,black_70%)]"></div>
    </div>
  );
});
export default DotBackground;
