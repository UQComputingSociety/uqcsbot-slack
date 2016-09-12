module Main (setup) where

import Prelude
import Control.Monad.Eff.Console (log)


scripts = [
]

setup r = do
  log "Hello, world!"
  pure unit
