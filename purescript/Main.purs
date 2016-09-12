module Main (setup) where

import Prelude
import Hubot (Robot)
import Control.Monad.Eff (Eff)
import Data.Foldable (traverse_)


type Script eff = Robot -> Eff (eff) Unit

scripts :: forall eff. Array (Script (eff))
scripts = [
]

setup :: forall eff. Script eff
setup r = traverse_ (\x -> x r) scripts
