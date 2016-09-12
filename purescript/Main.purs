module Main (setup) where

import Prelude
import Control.Monad.Eff.Console (log)
import Data.Foldable (traverse_)


scripts = [
]

setup r = traverse_ (\x -> x r) scripts
